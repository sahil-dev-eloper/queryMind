import uuid
from datetime import datetime
from typing import Optional

from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ConnectionStatus(str, Enum):
    UNTESTED = "untested"
    CONNECTED = "connected"
    FAILED = "failed"


class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    database_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_password: Mapped[str] = mapped_column(Text, nullable=False)
    ssl_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="prefer")
    last_tested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    connection_status: Mapped[str] = mapped_column(String(16), nullable=False, default=ConnectionStatus.UNTESTED.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[Optional["User"]] = relationship(back_populates="database_connections")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="database_connection", cascade="all, delete-orphan")
    schemas: Mapped[list["DatabaseSchema"]] = relationship(back_populates="database_connection", cascade="all, delete-orphan")

    @property
    def is_shared(self) -> bool:
        return self.user_id is None


class DatabaseSchema(Base):
    __tablename__ = "database_schemas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_connection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("database_connections.id", ondelete="CASCADE"), nullable=False)
    schema_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    database_connection: Mapped[DatabaseConnection] = relationship(back_populates="schemas")
    tables: Mapped[list["DatabaseTable"]] = relationship(back_populates="schema", cascade="all, delete-orphan")


class DatabaseTable(Base):
    __tablename__ = "database_tables"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_schema_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("database_schemas.id", ondelete="CASCADE"), nullable=False)
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    table_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    schema: Mapped[DatabaseSchema] = relationship(back_populates="tables")
    columns: Mapped[list["DatabaseColumn"]] = relationship(back_populates="table", cascade="all, delete-orphan")
    source_relationships: Mapped[list["DatabaseRelationship"]] = relationship(foreign_keys="DatabaseRelationship.source_table_id", back_populates="source_table", cascade="all, delete-orphan")
    target_relationships: Mapped[list["DatabaseRelationship"]] = relationship(foreign_keys="DatabaseRelationship.target_table_id", back_populates="target_table", cascade="all, delete-orphan")


class DatabaseColumn(Base):
    __tablename__ = "database_columns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_table_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("database_tables.id", ondelete="CASCADE"), nullable=False)
    column_name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(255), nullable=False)
    nullable: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_primary_key: Mapped[bool] = mapped_column(nullable=False, default=False)
    default_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    table: Mapped[DatabaseTable] = relationship(back_populates="columns")
    source_relationships: Mapped[list["DatabaseRelationship"]] = relationship(foreign_keys="DatabaseRelationship.source_column_id", back_populates="source_column")
    target_relationships: Mapped[list["DatabaseRelationship"]] = relationship(foreign_keys="DatabaseRelationship.target_column_id", back_populates="target_column")


class DatabaseRelationship(Base):
    __tablename__ = "database_relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_table_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("database_tables.id", ondelete="CASCADE"), nullable=False)
    source_column_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("database_columns.id", ondelete="CASCADE"), nullable=False)
    target_table_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("database_tables.id", ondelete="CASCADE"), nullable=False)
    target_column_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("database_columns.id", ondelete="CASCADE"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(32), nullable=False, default="foreign_key")

    source_table: Mapped[DatabaseTable] = relationship(foreign_keys=[source_table_id], back_populates="source_relationships")
    source_column: Mapped[DatabaseColumn] = relationship(foreign_keys=[source_column_id], back_populates="source_relationships")
    target_table: Mapped[DatabaseTable] = relationship(foreign_keys=[target_table_id], back_populates="target_relationships")
    target_column: Mapped[DatabaseColumn] = relationship(foreign_keys=[target_column_id], back_populates="target_relationships")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_connection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("database_connections.id"), nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_intent: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    current_state: Mapped[str] = mapped_column(String(32), nullable=False, default="analyzing")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[Optional["User"]] = relationship(back_populates="conversations")
    database_connection: Mapped[DatabaseConnection] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    query_executions: Mapped[list["QueryExecution"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    clarifications: Mapped[list["Clarification"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Clarification(Base):
    __tablename__ = "clarifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    field: Mapped[str] = mapped_column(String(64), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    round_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    conversation: Mapped[Conversation] = relationship(back_populates="clarifications")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class QueryExecution(Base):
    __tablename__ = "query_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id"), nullable=True)
    natural_language_query: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_intent: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    generated_sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_category: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    repair_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    repaired_sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation: Mapped[Conversation] = relationship(back_populates="query_executions")
    message: Mapped[Optional[Message]] = relationship()
