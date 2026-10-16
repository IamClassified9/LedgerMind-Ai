"""Create businesses and provisionable record templates.

Revision ID: 0001_business_onboarding
Revises:
Create Date: 2026-10-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import Uuid

revision: str = "0001_business_onboarding"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "businesses",
        sa.Column("id", Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("business_type", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="NGN", nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="Africa/Lagos", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "business_type IN ('restaurant', 'supermarket')",
            name="ck_businesses_business_type",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_businesses_name", "businesses", ["name"], unique=False)
    op.create_index("ix_businesses_business_type", "businesses", ["business_type"], unique=False)

    op.create_table(
        "record_templates",
        sa.Column("id", Uuid(as_uuid=True), nullable=False),
        sa.Column("business_id", Uuid(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("fields", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "key", name="uq_record_templates_business_key"),
    )
    op.create_index("ix_record_templates_business_id", "record_templates", ["business_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_record_templates_business_id", table_name="record_templates")
    op.drop_table("record_templates")
    op.drop_index("ix_businesses_business_type", table_name="businesses")
    op.drop_index("ix_businesses_name", table_name="businesses")
    op.drop_table("businesses")
