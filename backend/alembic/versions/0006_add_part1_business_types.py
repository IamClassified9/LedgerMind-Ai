"""Add remaining Part 1 template-only business types.

Revision ID: 0006_add_part1_business_types
Revises: 0005_add_trucking_business_type
"""
from typing import Sequence, Union
from alembic import op
revision: str = "0006_add_part1_business_types"
down_revision: Union[str, None] = "0005_add_trucking_business_type"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BUSINESS_TYPES = "'restaurant', 'supermarket', 'trucking', 'contractor', 'hotel', 'farm', 'rental_property', 'school', 'salon', 'training', 'pharmacy'"

def upgrade() -> None:
    op.drop_constraint("ck_businesses_business_type", "businesses", type_="check")
    op.create_check_constraint("ck_businesses_business_type", "businesses", f"business_type IN ({BUSINESS_TYPES})")

def downgrade() -> None:
    # Preserve data safety: operators must remove new business types before downgrading.
    op.drop_constraint("ck_businesses_business_type", "businesses", type_="check")
    op.create_check_constraint("ck_businesses_business_type", "businesses", "business_type IN ('restaurant', 'supermarket', 'trucking')")
