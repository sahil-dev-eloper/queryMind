from uuid import UUID

from pydantic import BaseModel, Field


class ClarificationOptionResponse(BaseModel):
    label: str
    value: str


class ClarificationResponse(BaseModel):
    id: UUID
    field: str
    question: str
    options: list[ClarificationOptionResponse]
    required: bool = True


class ConversationQueryRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ClarificationAnswerRequest(BaseModel):
    clarification_id: UUID
    answer: str = Field(min_length=1, max_length=1000)


class ConversationCreateRequest(BaseModel):
    database_id: UUID
    title: str | None = None


class ConversationResponse(BaseModel):
    id: UUID
    database_id: UUID
    state: str


class ConversationHistoryResponse(BaseModel):
    id: UUID
    database_id: UUID
    title: str
    state: str
    created_at: str
    updated_at: str
