from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DatabaseConnectionInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=5432, ge=1, le=65535)
    database_name: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)
    ssl_mode: str = Field(default="prefer", pattern="^(disable|allow|prefer|require|verify-ca|verify-full)$")


class DatabaseConnectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    host: str
    port: int
    database_name: str
    username: str
    ssl_mode: str
    created_at: datetime
    updated_at: datetime
    last_tested_at: datetime | None
    connection_status: str


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str


class IntrospectionResponse(BaseModel):
    success: bool
    tables: int
    columns: int
    relationships: int


class ColumnResponse(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool
    default_value: str | None = None
    foreign_key: str | None = None


class TableResponse(BaseModel):
    name: str
    type: str
    description: str | None = None
    columns: list[ColumnResponse]


class SchemaResponse(BaseModel):
    database_id: UUID
    database: str
    dialect: str
    schemas: list[dict]
