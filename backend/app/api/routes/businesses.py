from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import Business, RecordTemplate
from app.models.user import BusinessMembership, User
from app.security.auth import get_current_user, require_business_access
from app.schemas.business import (
    BusinessCreate,
    BusinessRead,
    BusinessTypeOption,
    RecordTemplateRead,
)
from app.services.business_templates import templates_for
from app.services.country_settings import country_settings, valid_timezone
from app.models.record_entry import RecordEntry
from app.models.supplier_invoice import SupplierInvoice
from pydantic import BaseModel, Field

router = APIRouter()

BUSINESS_TYPE_OPTIONS = [
    BusinessTypeOption(
        key="restaurant",
        label="Restaurant",
        description="Track sales, purchases, ingredients, stock movements, waste, and expenses.",
    ),
    BusinessTypeOption(
        key="supermarket",
        label="Supermarket",
        description="Track products, sales, supplier orders, deliveries, returns, stock counts, and expenses.",
    ),
    BusinessTypeOption(
        key="trucking",
        label="Transport / Trucking",
        description="Track trips, truck fleet, fuel and trip expenses, payments, maintenance, and drivers.",
    ),
    BusinessTypeOption(key="contractor", label="Contractor", description="Track jobs, contracts, project costs, quotes, invoices, and collections."),
    BusinessTypeOption(key="hotel", label="Hotel", description="Track bookings, rooms, guest payments, and operating expenses."),
    BusinessTypeOption(key="farm", label="Farm", description="Choose crops, livestock, poultry, or any combination, alongside shared farm records."),
    BusinessTypeOption(key="rental_property", label="Rental Property", description="Track properties, tenants, rent due, occupancy, and maintenance."),
    BusinessTypeOption(key="school", label="School", description="Track students, fees, attendance, and balances."),
    BusinessTypeOption(key="salon", label="Salon", description="Track appointments, services, products, staff, and expenses."),
    BusinessTypeOption(key="training", label="Training / Courses", description="Track courses, cohorts, learners, fee payments, and expenses."),
    BusinessTypeOption(key="pharmacy", label="Pharmacy", description="Track product stock, batch and expiry dates, sales, and supplier purchases."),
]


@router.get("/business-types", response_model=list[BusinessTypeOption], summary="List supported business types")
def list_business_types() -> list[BusinessTypeOption]:
    return BUSINESS_TYPE_OPTIONS


@router.get("/businesses", response_model=list[BusinessRead], summary="List businesses available to the current user")
def list_businesses(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Business]:
    statement = (
        select(Business)
        .join(BusinessMembership, BusinessMembership.business_id == Business.id)
        .where(BusinessMembership.user_id == user.id)
        .order_by(Business.created_at.asc(), Business.name.asc())
    )
    return list(db.scalars(statement).all())


@router.post(
    "/businesses",
    response_model=BusinessRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a business and provision its starter templates",
)
def create_business(payload: BusinessCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Business:
    try:
        country = country_settings(payload.country)
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    timezone_name = valid_timezone(payload.timezone)
    if timezone_name == "UTC" and payload.timezone != "UTC":
        timezone_name = country["timezones"][0]
    if timezone_name not in country["timezones"] and len(country["timezones"]) == 1:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Choose a valid time zone for the selected country.")
    if payload.currency.upper() != country["currency"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Currency is determined by the selected country.")
    business = Business(
        name=payload.name,
        business_type=payload.business_type,
        country=payload.country.upper(),
        currency=country["currency"],
        timezone=timezone_name,
    )
    db.add(business)
    db.flush()
    db.add(BusinessMembership(user_id=user.id, business_id=business.id, role="owner"))

    for definition in templates_for(payload.business_type, payload.farm_modules):
        db.add(
            RecordTemplate(
                business_id=business.id,
                key=definition["key"],
                name=definition["name"],
                description=definition["description"],
                fields=definition["fields"],
            )
        )

    db.commit()
    db.refresh(business)
    return business


class BusinessSettingsUpdate(BaseModel):
    country: str = Field(min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$")
    currency: str = Field(min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")
    timezone: str = Field(min_length=1, max_length=64)


@router.patch("/businesses/{business_id}/settings", response_model=BusinessRead)
def update_business_settings(business_id: UUID, payload: BusinessSettingsUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Business:
    business = require_business_access(db, user, business_id)
    try:
        country = country_settings(payload.country)
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    timezone_name = valid_timezone(payload.timezone)
    if timezone_name not in country["timezones"] and len(country["timezones"]) == 1:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Choose a valid time zone for the selected country.")
    if payload.currency.upper() != country["currency"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Currency is determined by the selected country.")
    if business.currency != country["currency"]:
        records_exist = db.scalar(select(RecordEntry.id).where(RecordEntry.business_id == business_id).limit(1)) is not None
        invoices_exist = db.scalar(select(SupplierInvoice.id).where(SupplierInvoice.business_id == business_id).limit(1)) is not None
        if records_exist or invoices_exist:
            from fastapi import HTTPException
            raise HTTPException(status_code=409, detail="Business currency is locked after the first record or supplier invoice.")
    business.country = payload.country.upper()
    business.currency = country["currency"]
    business.timezone = timezone_name
    db.commit()
    db.refresh(business)
    return business


@router.get("/businesses/{business_id}", response_model=BusinessRead, summary="Get a business")
def get_business(business_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Business:
    return require_business_access(db, user, business_id)


@router.get(
    "/businesses/{business_id}/templates",
    response_model=list[RecordTemplateRead],
    summary="List a business's record templates",
)
def list_business_templates(business_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[RecordTemplate]:
    require_business_access(db, user, business_id)
    statement = (
        select(RecordTemplate)
        .where(RecordTemplate.business_id == business_id)
        .order_by(RecordTemplate.name.asc())
    )
    return list(db.scalars(statement).all())
