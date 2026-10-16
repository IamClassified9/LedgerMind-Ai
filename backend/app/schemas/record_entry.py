from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecordEntryCreate(BaseModel):
    values: dict[str, Any] = Field(min_length=1)


class RecordEntryUpdate(BaseModel):
    values: dict[str, Any] = Field(min_length=1)


class RecordEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    template_id: UUID
    values: dict[str, Any]
    created_at: datetime
    updated_at: datetime
