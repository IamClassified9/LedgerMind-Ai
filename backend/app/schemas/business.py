from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

BusinessType = Literal["restaurant", "supermarket", "trucking", "contractor", "hotel", "farm", "rental_property", "school", "salon", "training", "pharmacy"]


class BusinessCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    business_type: BusinessType
    country: str = Field(default="NG", min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$")
    currency: str = Field(default="NGN", min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")
    timezone: str = Field(default="Africa/Lagos", min_length=1, max_length=64)
    farm_modules: list[Literal["crops", "livestock", "poultry"]] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Business name must contain at least 2 non-space characters.")
        return normalized

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return value.upper()

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class BusinessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    business_type: BusinessType
    country: str
    currency: str
    timezone: str
    created_at: datetime
    updated_at: datetime


class RecordTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    key: str
    name: str
    description: str
    fields: list[dict[str, Any]]
    created_at: datetime


class BusinessTypeOption(BaseModel):
    key: BusinessType
    label: str
    description: str
