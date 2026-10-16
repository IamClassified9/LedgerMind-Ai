"""Add business country with backward-compatible defaults.

Revision ID: 0007_business_country
Revises: 0006_add_part1_business_types
"""
from alembic import op
import sqlalchemy as sa
revision = "0007_business_country"
down_revision = "0006_add_part1_business_types"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("businesses", sa.Column("country", sa.String(length=2), nullable=False, server_default="NG"))
    op.alter_column("businesses", "currency", existing_type=sa.String(length=3), server_default="NGN", nullable=False)
    op.alter_column("businesses", "timezone", existing_type=sa.String(length=64), server_default="Africa/Lagos", nullable=False)

def downgrade() -> None:
    op.drop_column("businesses", "country")
