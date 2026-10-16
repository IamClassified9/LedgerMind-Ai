"""Create persisted business record entries.

Revision ID: 0002_daily_records
Revises: 0001_business_onboarding
Create Date: 2026-10-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import Uuid

revision: str = "0002_daily_records"
down_revision: Union[str, None] = "0001_business_onboarding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "record_entries",
        sa.Column("id", Uuid(as_uuid=True), nullable=False),
        sa.Column("business_id", Uuid(as_uuid=True), nullable=False),
        sa.Column("template_id", Uuid(as_uuid=True), nullable=False),
        sa.Column("values", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["record_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_record_entries_business_id", "record_entries", ["business_id"], unique=False)
    op.create_index("ix_record_entries_template_id", "record_entries", ["template_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_record_entries_template_id", table_name="record_entries")
    op.drop_index("ix_record_entries_business_id", table_name="record_entries")
    op.drop_table("record_entries")
