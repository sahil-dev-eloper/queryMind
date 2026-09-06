from enum import Enum


class ConversationState(str, Enum):
    ANALYZING = "analyzing"
    CLARIFICATION_REQUIRED = "clarification_required"
    WAITING_FOR_ANSWER = "waiting_for_answer"
    RESOLVING = "resolving"
    READY_FOR_SQL = "ready_for_sql"
    GENERATING_SQL = "generating_sql"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
