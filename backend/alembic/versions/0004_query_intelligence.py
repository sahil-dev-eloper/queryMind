"""Add query repair and result analysis metadata."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_query_intelligence"
down_revision = "0003_clarification_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("query_executions", sa.Column("error_category", sa.String(length=32), nullable=True))
    op.add_column("query_executions", sa.Column("repair_attempts", sa.Integer(), server_default="0", nullable=False))
    op.add_column("query_executions", sa.Column("repaired_sql", sa.Text(), nullable=True))
    op.add_column("query_executions", sa.Column("result_analysis", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column("query_executions", "result_analysis")
    op.drop_column("query_executions", "repaired_sql")
    op.drop_column("query_executions", "repair_attempts")
    op.drop_column("query_executions", "error_category")
