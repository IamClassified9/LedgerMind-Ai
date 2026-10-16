from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import RecordTemplate
from app.models.record_entry import RecordEntry
from app.models.supplier_invoice import SupplierInvoice
from app.models.user import User
from app.security.auth import get_current_user, require_business_access
from app.schemas.record_entry import RecordEntryCreate, RecordEntryRead, RecordEntryUpdate
from app.schemas.supplier_invoice import SupplierInvoiceCreate, SupplierInvoiceRead
from app.services.record_validation import validate_record_values

router = APIRouter()


def _get_template(db: Session, business_id: UUID, template_id: UUID) -> RecordTemplate:
    template = db.scalar(
        select(RecordTemplate).where(
            RecordTemplate.id == template_id,
            RecordTemplate.business_id == business_id,
        )
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Record template not found for this business.")
    return template


def _get_record(db: Session, business_id: UUID, record_id: UUID) -> RecordEntry:
    record = db.scalar(
        select(RecordEntry).where(
            RecordEntry.id == record_id,
            RecordEntry.business_id == business_id,
        )
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found for this business.")
    return record


@router.post(
    "/businesses/{business_id}/templates/{template_id}/records",
    response_model=RecordEntryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a validated business record",
)
def create_record(
    business_id: UUID,
    template_id: UUID,
    payload: RecordEntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecordEntry:
    require_business_access(db, user, business_id)
    template = _get_template(db, business_id, template_id)
    validated = validate_record_values(template.fields, payload.values)
    record = RecordEntry(business_id=business_id, template_id=template_id, values=validated)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get(
    "/businesses/{business_id}/records",
    response_model=list[RecordEntryRead],
    summary="List a business's records",
)
def list_records(
    business_id: UUID,
    template_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[RecordEntry]:
    require_business_access(db, user, business_id)
    statement = select(RecordEntry).where(RecordEntry.business_id == business_id)
    if template_id is not None:
        _get_template(db, business_id, template_id)
        statement = statement.where(RecordEntry.template_id == template_id)
    statement = statement.order_by(RecordEntry.created_at.desc(), RecordEntry.id).limit(limit).offset(offset)
    return list(db.scalars(statement).all())


@router.get(
    "/businesses/{business_id}/records/{record_id}",
    response_model=RecordEntryRead,
    summary="Get a business record",
)
def get_record(business_id: UUID, record_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> RecordEntry:
    require_business_access(db, user, business_id)
    return _get_record(db, business_id, record_id)


@router.patch(
    "/businesses/{business_id}/records/{record_id}",
    response_model=RecordEntryRead,
    summary="Update a business record",
)
def update_record(
    business_id: UUID,
    record_id: UUID,
    payload: RecordEntryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RecordEntry:
    require_business_access(db, user, business_id)
    record = _get_record(db, business_id, record_id)
    template = _get_template(db, business_id, record.template_id)
    merged = {**record.values, **payload.values}
    record.values = validate_record_values(template.fields, merged)
    db.commit()
    db.refresh(record)
    return record


@router.delete(
    "/businesses/{business_id}/records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a business record",
)
def delete_record(business_id: UUID, record_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    require_business_access(db, user, business_id)
    record = _get_record(db, business_id, record_id)
    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/businesses/{business_id}/supplier-invoices",
    response_model=list[SupplierInvoiceRead],
    summary="List confirmed supplier invoices for a business",
)
def list_supplier_invoices(
    business_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SupplierInvoice]:
    require_business_access(db, user, business_id)
    statement = (
        select(SupplierInvoice)
        .where(SupplierInvoice.business_id == business_id)
        .order_by(SupplierInvoice.transaction_date.desc(), SupplierInvoice.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.post(
    "/businesses/{business_id}/supplier-invoices",
    response_model=SupplierInvoiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Save a human-reviewed supplier invoice",
)
def create_supplier_invoice(
    business_id: UUID,
    payload: SupplierInvoiceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SupplierInvoice:
    business = require_business_access(db, user, business_id)
    supplier = payload.supplier.strip()
    if not supplier:
        raise HTTPException(status_code=422, detail="Supplier name is required.")
    invoice = SupplierInvoice(
        business_id=business.id,
        created_by_user_id=user.id,
        supplier=supplier,
        invoice_amount=payload.invoice_amount,
        amount_paid=payload.amount_paid,
        currency=business.currency,
        transaction_date=payload.transaction_date,
        reference=payload.reference.strip() if payload.reference else None,
        direction=payload.direction,
        note=payload.note.strip() if payload.note else None,
        source_note=payload.source_note.strip() if payload.source_note else None,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice
