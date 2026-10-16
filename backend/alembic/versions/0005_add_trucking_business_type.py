"""Allow trucking businesses without changing existing business records.

Revision ID: 0005_add_trucking_business_type
Revises: 0004_supplier_invoices
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0005_add_trucking_business_type"
down_revision: Union[str, None] = "0004_supplier_invoices"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_businesses_business_type", "businesses", type_="check")
    op.create_check_constraint(
        "ck_businesses_business_type",
        "businesses",
        "business_type IN ('restaurant', 'supermarket', 'trucking')",
    )


def downgrade() -> None:
    # Do not silently invalidate data: remove trucking businesses before downgrade.
    op.drop_constraint("ck_businesses_business_type", "businesses", type_="check")
    op.create_check_constraint(
        "ck_businesses_business_type",
        "businesses",
        "business_type IN ('restaurant', 'supermarket')",
    )
