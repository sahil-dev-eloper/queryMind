"""Persist clarification sessions and conversation state."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_clarification_state"
down_revision = "0002_external_schema_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("original_query", sa.Text(), nullable=True))
    op.add_column("conversations", sa.Column("current_intent", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("conversations", sa.Column("current_state", sa.String(length=32), server_default="analyzing", nullable=False))
    op.create_table("clarifications", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("field", sa.String(length=64), nullable=False), sa.Column("question", sa.Text(), nullable=False), sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=False), sa.Column("answer", sa.Text(), nullable=True), sa.Column("status", sa.String(length=16), nullable=False), sa.Column("round_number", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))


def downgrade() -> None:
    op.drop_table("clarifications")
    op.drop_column("conversations", "current_state")
    op.drop_column("conversations", "current_intent")
    op.drop_column("conversations", "original_query")
