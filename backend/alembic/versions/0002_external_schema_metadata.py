"""Add external connection status and persisted schema metadata."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_external_schema_metadata"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("database_connections", sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("database_connections", sa.Column("connection_status", sa.String(length=16), server_default="untested", nullable=False))
    op.create_table("database_schemas", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("database_connection_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("schema_name", sa.String(length=255), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["database_connection_id"], ["database_connections.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_table("database_tables", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("database_schema_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("table_name", sa.String(length=255), nullable=False), sa.Column("table_type", sa.String(length=32), nullable=False), sa.Column("description", sa.Text(), nullable=True), sa.ForeignKeyConstraint(["database_schema_id"], ["database_schemas.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_table("database_columns", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("database_table_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("column_name", sa.String(length=255), nullable=False), sa.Column("data_type", sa.String(length=255), nullable=False), sa.Column("nullable", sa.Boolean(), nullable=False), sa.Column("is_primary_key", sa.Boolean(), nullable=False), sa.Column("default_value", sa.Text(), nullable=True), sa.Column("description", sa.Text(), nullable=True), sa.ForeignKeyConstraint(["database_table_id"], ["database_tables.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_table("database_relationships", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("source_table_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("source_column_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("target_table_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("target_column_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("relationship_type", sa.String(length=32), nullable=False), sa.ForeignKeyConstraint(["source_table_id"], ["database_tables.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["source_column_id"], ["database_columns.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["target_table_id"], ["database_tables.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["target_column_id"], ["database_columns.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))


def downgrade() -> None:
    op.drop_table("database_relationships")
    op.drop_table("database_columns")
    op.drop_table("database_tables")
    op.drop_table("database_schemas")
    op.drop_column("database_connections", "connection_status")
    op.drop_column("database_connections", "last_tested_at")
