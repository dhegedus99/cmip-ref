"""result-assest

Revision ID: c4874385133e
Revises: 6634396f139a
Create Date: 2025-03-06 12:24:54.518884

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4874385133e"
down_revision: Union[str, None] = "6634396f139a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "metric_execution_result_asset",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("metric_execution_result_id", sa.Integer(), nullable=False),
        sa.Column("asset_type", sa.Enum("Plot", "Data", "HTML", name="asset_type"), nullable=False),
        sa.Column("filename", sa.String(), nullable=True),
        sa.Column("long_name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(
            ["metric_execution_result_id"],
            ["metric_execution_result.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("metric_execution_result_asset", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_metric_execution_result_asset_asset_type"), ["asset_type"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_metric_execution_result_asset_metric_execution_result_id"),
            ["metric_execution_result_id"],
            unique=False,
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("metric_execution_result_asset", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_metric_execution_result_asset_metric_execution_result_id"))
        batch_op.drop_index(batch_op.f("ix_metric_execution_result_asset_asset_type"))

    op.drop_table("metric_execution_result_asset")
    # ### end Alembic commands ###
