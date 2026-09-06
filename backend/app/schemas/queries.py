from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)


class QueryResponse(BaseModel):
    status: str
    analysis: dict | None = None
    conversation_id: str | None = None
    clarification: dict | None = None
    rejection_reason: str | None = None
    sql: str | None = None
    explanation: str | None = None
    results: dict | None = None
    result_analysis: dict | None = None
    repair_attempts: int = 0

