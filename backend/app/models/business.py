from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class Business(Base):
    __tablename__ = "businesses"
    __table_args__ = (
        CheckConstraint(
            "business_type IN ('restaurant', 'supermarket', 'trucking', 'contractor', 'hotel', 'farm', 'rental_property', 'school', 'salon', 'training', 'pharmacy')",
            name="ck_businesses_business_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    business_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False, default="NG", server_default="NG")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="NGN", server_default="NGN")
    timezone: Mapped[str] = mapped_column(
        String(64), nullable=False, default="Africa/Lagos", server_default="Africa/Lagos"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    templates: Mapped[list[RecordTemplate]] = relationship(
        back_populates="business", cascade="all, delete-orphan", passive_deletes=True
    )


class RecordTemplate(Base):
    __tablename__ = "record_templates"
    __table_args__ = (
        UniqueConstraint("business_id", "key", name="uq_record_templates_business_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    fields: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    business: Mapped[Business] = relationship(back_populates="templates")
