from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SupplierInvoiceCreate(BaseModel):
    supplier: str = Field(min_length=1, max_length=200)
    invoice_amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    amount_paid: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    currency: str = Field(default="NGN", min_length=3, max_length=3)
    transaction_date: date
    reference: str | None = Field(default=None, max_length=120)
    direction: str = Field(default="business_owes_party", pattern="^(business_owes_party|party_owes_business|unknown)$")
    note: str | None = Field(default=None, max_length=5000)
    source_note: str | None = Field(default=None, max_length=20000)

    @model_validator(mode="after")
    def validate_payment(self):
        if self.amount_paid < 0:
            raise ValueError("amount_paid cannot be negative")
        return self


class SupplierInvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    created_by_user_id: UUID
    supplier: str
    invoice_amount: Decimal
    amount_paid: Decimal
    outstanding_amount: Decimal
    currency: str
    transaction_date: date
    reference: str | None
    direction: str
    note: str | None
    source_note: str | None
    created_at: datetime

