from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.database import Clarification, Conversation, DatabaseConnection
from app.schemas.clarifications import ClarificationAnswerRequest, ConversationCreateRequest, ConversationHistoryResponse, ConversationResponse, ConversationQueryRequest
from app.schemas.queries import QueryRequest, QueryResponse
from app.services.query_pipeline import QueryPipelineError, query_pipeline

router = APIRouter(prefix="/databases", tags=["queries"])
conversation_router = APIRouter(prefix="/conversations", tags=["conversations"])


@conversation_router.get("", response_model=list[ConversationHistoryResponse])
def list_conversations(db: Session = Depends(get_db)) -> list[ConversationHistoryResponse]:
    return [ConversationHistoryResponse(id=item.id, database_id=item.database_connection_id, title=item.title, state=item.current_state, created_at=item.created_at.isoformat() if item.created_at else "", updated_at=item.updated_at.isoformat() if item.updated_at else "") for item in db.query(Conversation).order_by(Conversation.updated_at.desc()).all()]


@conversation_router.get("/{conversation_id}")
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db)) -> dict:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"id": conversation.id, "database_id": conversation.database_connection_id, "title": conversation.title, "state": conversation.current_state, "messages": [{"role": message.role, "content": message.content, "created_at": message.created_at.isoformat() if message.created_at else ""} for message in conversation.messages], "intent": conversation.current_intent}


@router.post("/{database_id}/query", response_model=QueryResponse)
async def run_query(database_id: UUID, payload: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    connection = db.get(DatabaseConnection, database_id)
    if connection is None:
        raise HTTPException(status_code=404, detail="Database connection not found.")
    try:
        return QueryResponse.model_validate(await query_pipeline.run(db, connection, payload.query))
    except QueryPipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{database_id}/conversations", response_model=ConversationResponse)
def create_conversation(database_id: UUID, payload: ConversationCreateRequest, db: Session = Depends(get_db)) -> ConversationResponse:
    if payload.database_id != database_id or db.get(DatabaseConnection, database_id) is None:
        raise HTTPException(status_code=404, detail="Database connection not found.")
    conversation = Conversation(database_connection_id=database_id, title=payload.title or "New conversation")
    db.add(conversation)
    db.commit()
    return ConversationResponse(id=conversation.id, database_id=database_id, state=conversation.current_state)


@conversation_router.post("/{conversation_id}/query", response_model=QueryResponse)
async def run_conversation_query(conversation_id: UUID, payload: ConversationQueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    connection = db.get(DatabaseConnection, conversation.database_connection_id)
    try:
        return QueryResponse.model_validate(await query_pipeline.start(db, conversation, connection, payload.message))
    except QueryPipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@conversation_router.post("/{conversation_id}/clarification", response_model=QueryResponse)
async def answer_clarification(conversation_id: UUID, payload: ClarificationAnswerRequest, db: Session = Depends(get_db)) -> QueryResponse:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    clarification = db.get(Clarification, payload.clarification_id)
    if clarification is None or clarification.conversation_id != conversation.id:
        raise HTTPException(status_code=404, detail="Clarification not found.")
    connection = db.get(DatabaseConnection, conversation.database_connection_id)
    try:
        return QueryResponse.model_validate(await query_pipeline.answer(db, conversation, connection, clarification, payload.answer))
    except QueryPipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
