import logging
from datetime import date

from sqlalchemy.orm import Session

from app.ai.factory import get_ai_provider
from app.ai.models import Ambiguity, QueryAnalysis, TimeRange
from app.ai.provider import AIProviderError
from app.core.config import settings
from app.models.database import Clarification, Conversation, DatabaseConnection, Message, QueryExecution
from app.services.clarification import ClarificationError, clarification_answer_processor, clarification_question_generator
from app.services.clarification_state import ConversationState
from app.services.query_executor import QueryExecutionError, query_executor
from app.services.result_analyzer import result_analyzer
from app.services.sql_repair import SQLRepairError, sql_repair_service
from app.services.intent_modifier import intent_modifier
from app.services.schema_retriever import schema_retriever
from app.services.schema_serializer import serialize_schema
from app.services.sql_validator import SQLValidationError, sql_validator

logger = logging.getLogger(__name__)


class QueryPipelineError(Exception):
    pass


class QueryPipeline:
    async def run(self, db: Session, connection: DatabaseConnection, query: str, user_id=None) -> dict:
        conversation = Conversation(database_connection_id=connection.id, user_id=user_id, title=query[:255], original_query=query, current_state=ConversationState.ANALYZING.value)
        db.add(conversation)
        db.flush()
        db.add(Message(conversation_id=conversation.id, role="user", content=query))
        db.flush()
        result = await self._start(db, connection, conversation, query)
        return {"conversation_id": str(conversation.id), **result}

    async def start(self, db: Session, conversation: Conversation, connection: DatabaseConnection, query: str) -> dict:
        if conversation.current_state == ConversationState.COMPLETED.value and conversation.current_intent:
            analysis = intent_modifier.apply(QueryAnalysis.model_validate(conversation.current_intent), query)
            db.add(Message(conversation_id=conversation.id, role="user", content=query, message_metadata={"follow_up": True}))
            execution = QueryExecution(conversation_id=conversation.id, natural_language_query=query, status="processing", resolved_intent=analysis.model_dump(mode="json"))
            db.add(execution)
            db.flush()
            return {"conversation_id": str(conversation.id), **await self._execute_resolved(db, connection, conversation, execution, analysis, serialize_schema(db, connection))}
        conversation.original_query = query
        conversation.current_state = ConversationState.ANALYZING.value
        db.add(Message(conversation_id=conversation.id, role="user", content=query))
        db.flush()
        return {"conversation_id": str(conversation.id), **await self._start(db, connection, conversation, query)}

    async def answer(self, db: Session, conversation: Conversation, connection: DatabaseConnection, clarification: Clarification, answer: str) -> dict:
        if conversation.current_state != ConversationState.WAITING_FOR_ANSWER.value or clarification.status != "pending":
            raise QueryPipelineError("This clarification is no longer active.")
        db.add(Message(conversation_id=conversation.id, role="user", content=answer, message_metadata={"clarification_id": str(clarification.id)}))
        analysis = QueryAnalysis.model_validate(conversation.current_intent or {})
        try:
            clarification_answer_processor.process(clarification, answer, analysis)
        except ClarificationError as exc:
            db.commit()
            raise QueryPipelineError(str(exc)) from exc
        if clarification.field == "metric" and not self._has_explicit_time(conversation.original_query or ""):
            analysis.ambiguities.append(Ambiguity(field="time_range", reason="No time period was specified for this ranking."))
        conversation.current_intent = analysis.model_dump(mode="json")
        execution = db.query(QueryExecution).filter(QueryExecution.conversation_id == conversation.id).order_by(QueryExecution.created_at.desc()).first()
        schema = serialize_schema(db, connection)
        prompt = clarification_question_generator.generate(analysis, schema, len(conversation.clarifications) + 1)
        if analysis.ambiguities and prompt:
            return self._save_clarification(db, conversation, execution, analysis, prompt)
        if clarification.round_number >= 3:
            conversation.current_state = ConversationState.FAILED.value
            db.commit()
            raise QueryPipelineError("I couldn't determine the remaining requirements confidently enough to generate a safe query.")
        try:
            return await self._execute_resolved(db, connection, conversation, execution, analysis, schema)
        except (AIProviderError, QueryExecutionError, SQLValidationError, SQLRepairError, ValueError) as exc:
            execution.status = "failed"
            execution.error = str(exc)
            conversation.current_state = ConversationState.FAILED.value
            db.commit()
            logger.warning("Clarified query failed", extra={"database_id": str(connection.id), "error_type": type(exc).__name__})
            raise QueryPipelineError("The query could not be completed safely.") from exc

    async def _start(self, db: Session, connection: DatabaseConnection, conversation: Conversation, query: str) -> dict:
        execution = QueryExecution(conversation_id=conversation.id, natural_language_query=query, status="processing")
        db.add(execution)
        db.flush()
        try:
            schema = serialize_schema(db, connection)
            ranked = schema_retriever.retrieve(db, str(connection.id), query)
            relevant_schema = self._filter_schema(schema, {item["table"] for item in ranked}) if ranked else schema
            analysis = await get_ai_provider().analyze_query(query, relevant_schema, "postgresql")
            conversation.current_intent = analysis.model_dump(mode="json")
            if not analysis.is_answerable:
                execution.status = "rejected"
                execution.error = analysis.rejection_reason or "This question doesn't appear to be related to your database."
                conversation.current_state = ConversationState.COMPLETED.value
                db.commit()
                return {"status": "rejected", "rejection_reason": analysis.rejection_reason or "This question doesn't appear to be related to your database.", "conversation_id": str(conversation.id)}
            if analysis.is_ambiguous:
                prompt = clarification_question_generator.generate(analysis, relevant_schema, 1)
                if prompt:
                    return self._save_clarification(db, conversation, execution, analysis, prompt)
            return await self._execute_resolved(db, connection, conversation, execution, analysis, relevant_schema)
        except (AIProviderError, QueryExecutionError, SQLValidationError, ValueError) as exc:
            execution.status = "failed"
            execution.error = str(exc)
            conversation.current_state = ConversationState.FAILED.value
            db.commit()
            logger.warning("Query pipeline failed: %s: %s", type(exc).__name__, str(exc), extra={"database_id": str(connection.id), "error_type": type(exc).__name__})
            raise QueryPipelineError("The query could not be completed safely.") from exc

    async def _execute_resolved(self, db: Session, connection: DatabaseConnection, conversation: Conversation, execution: QueryExecution, analysis: QueryAnalysis, schema: dict) -> dict:
        ranked = schema_retriever.retrieve(db, str(connection.id), conversation.original_query or "")
        relevant_schema = self._filter_schema(schema, {item["table"] for item in ranked}) if ranked else schema
        conversation.current_state = ConversationState.GENERATING_SQL.value
        generated = await get_ai_provider().generate_sql(conversation.original_query or "", analysis, relevant_schema, "postgresql")
        sql_validator.validate(generated.sql, relevant_schema)
        conversation.current_state = ConversationState.EXECUTING.value
        repair_attempts = 0
        try:
            results = query_executor.execute(connection, generated.sql, relevant_schema)
        except QueryExecutionError as exc:
            while repair_attempts < settings.max_sql_repair_attempts:
                repair_attempts += 1
                try:
                    generated.sql = sql_repair_service.repair(generated.sql, str(exc), relevant_schema)
                    results = query_executor.execute(connection, generated.sql, relevant_schema)
                    execution.repaired_sql = generated.sql
                    break
                except (QueryExecutionError, SQLRepairError):
                    continue
            else:
                execution.error_category = exc.category.value
                execution.repair_attempts = repair_attempts
                raise
        analysis_result = result_analyzer.analyze(results["columns"], results["rows"])
        execution.resolved_intent = analysis.model_dump(mode="json")
        execution.generated_sql = generated.sql
        execution.status = "completed"
        execution.execution_time_ms = results["execution_time_ms"]
        execution.row_count = results["row_count"]
        execution.result_analysis = analysis_result
        execution.repair_attempts = repair_attempts
        conversation.current_state = ConversationState.COMPLETED.value
        db.commit()
        return {"status": "completed", "analysis": analysis.model_dump(mode="json"), "sql": generated.sql, "explanation": generated.explanation, "results": results, "result_analysis": analysis_result, "repair_attempts": repair_attempts, "conversation_id": str(conversation.id)}

    def _save_clarification(self, db: Session, conversation: Conversation, execution: QueryExecution, analysis: QueryAnalysis, prompt) -> dict:
        conversation.current_state = ConversationState.WAITING_FOR_ANSWER.value
        execution.resolved_intent = analysis.model_dump(mode="json")
        execution.status = "clarification_required"
        clarification = Clarification(conversation_id=conversation.id, field=prompt.field, question=prompt.question, options=[{"label": option.label, "value": option.value} for option in prompt.options], round_number=len(conversation.clarifications) + 1)
        db.add(clarification)
        db.flush()
        db.add(Message(conversation_id=conversation.id, role="assistant", content=prompt.question, message_metadata={"clarification_id": str(clarification.id), "options": clarification.options}))
        db.commit()
        return {"status": "clarification_required", "analysis": analysis.model_dump(mode="json"), "clarification": {"id": str(clarification.id), "field": prompt.field, "question": prompt.question, "options": clarification.options, "required": True}, "conversation_id": str(conversation.id)}

    @staticmethod
    def _has_explicit_time(query: str) -> bool:
        text = query.lower()
        return any(token in text for token in ("today", "yesterday", "week", "month", "quarter", "year", "202", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"))

    @staticmethod
    def _filter_schema(schema: dict, table_names: set[str]) -> dict:
        return {**schema, "schemas": [{"name": item["name"], "tables": [table for table in item["tables"] if table["name"] in table_names]} for item in schema["schemas"] if any(table["name"] in table_names for table in item["tables"])]}


query_pipeline = QueryPipeline()
