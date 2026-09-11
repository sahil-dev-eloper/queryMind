"""user authentication

Revision ID: 0005
Revises: 0004_query_intelligence
Create Date: 2026-09-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004_query_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column("database_connections", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_database_connections_user_id", "database_connections", ["user_id"])
    op.create_foreign_key("fk_database_connections_user_id", "database_connections", "users", ["user_id"], ["id"])

    op.add_column("conversations", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])
    op.create_foreign_key("fk_conversations_user_id", "conversations", "users", ["user_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_conversations_user_id", "conversations", type_="foreignkey")
    op.drop_index("ix_conversations_user_id", "conversations")
    op.drop_column("conversations", "user_id")

    op.drop_constraint("fk_database_connections_user_id", "database_connections", type_="foreignkey")
    op.drop_index("ix_database_connections_user_id", "database_connections")
    op.drop_column("database_connections", "user_id")

    op.drop_table("users")
