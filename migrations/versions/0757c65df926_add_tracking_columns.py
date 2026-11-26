"""add_tracking_columns

Revision ID: 0757c65df926
Revises: e5455a9a802c
Create Date: 2026-11-26 10:57:38.843934

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0757c65df926"
down_revision: Union[str, Sequence[str], None] = "e5455a9a802c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "evaluation_attempts",
        sa.Column("agent_id", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "evaluation_attempts",
        sa.Column("model_name", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "evaluation_attempts",
        sa.Column("batch_id", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "evaluation_attempts",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )
    op.add_column(
        "evaluation_attempts", sa.Column("status", sa.String(length=20), nullable=True)
    )
    op.add_column(
        "evaluation_attempts", sa.Column("error_message", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("evaluation_attempts", "error_message")
    op.drop_column("evaluation_attempts", "status")
    op.drop_column("evaluation_attempts", "created_at")
    op.drop_column("evaluation_attempts", "batch_id")
    op.drop_column("evaluation_attempts", "model_name")
    op.drop_column("evaluation_attempts", "agent_id")
