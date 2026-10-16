"""Add human-confirmed supplier invoice records.

Revision ID: 0004_supplier_invoices
Revises: 0003_authentication
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import Uuid

revision: str = "0004_supplier_invoices"
down_revision: Union[str, None] = "0003_authentication"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "supplier_invoices",
        sa.Column("id", Uuid(as_uuid=True), nullable=False),
        sa.Column("business_id", Uuid(as_uuid=True), nullable=False),
        sa.Column("created_by_user_id", Uuid(as_uuid=True), nullable=False),
        sa.Column("supplier", sa.String(length=200), nullable=False),
        sa.Column("invoice_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("amount_paid", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="NGN", nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("reference", sa.String(length=120), nullable=True),
        sa.Column("direction", sa.String(length=40), server_default="business_owes_party", nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("source_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("invoice_amount >= 0", name="ck_supplier_invoices_invoice_amount_nonnegative"),
        sa.CheckConstraint("amount_paid >= 0", name="ck_supplier_invoices_amount_paid_nonnegative"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_supplier_invoices_business_id", "supplier_invoices", ["business_id"])
    op.create_index("ix_supplier_invoices_created_by_user_id", "supplier_invoices", ["created_by_user_id"])
    op.create_index("ix_supplier_invoices_transaction_date", "supplier_invoices", ["transaction_date"])


def downgrade() -> None:
    op.drop_index("ix_supplier_invoices_transaction_date", table_name="supplier_invoices")
    op.drop_index("ix_supplier_invoices_created_by_user_id", table_name="supplier_invoices")
    op.drop_index("ix_supplier_invoices_business_id", table_name="supplier_invoices")
    op.drop_table("supplier_invoices")
