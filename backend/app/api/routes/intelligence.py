from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import RecordTemplate
from app.models.record_entry import RecordEntry
from app.models.user import User
from app.security.auth import get_current_user, require_business_access

router = APIRouter()


def _normal(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().casefold().split())


def _decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return number if number.is_finite() else None


@router.get(
    "/businesses/{business_id}/intelligence/issues",
    tags=["intelligence"],
    summary="Find evidence-based business record issues",
)
def intelligence_issues(
    business_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return deterministic review flags; this endpoint never changes records."""
    business = require_business_access(db, user, business_id)

    rows = db.execute(
        select(RecordEntry, RecordTemplate)
        .join(RecordTemplate, RecordEntry.template_id == RecordTemplate.id)
        .where(
            RecordEntry.business_id == business_id,
            RecordTemplate.business_id == business_id,
        )
        .order_by(RecordEntry.created_at.asc(), RecordEntry.id.asc())
    ).all()

    issues: list[dict[str, Any]] = []
    duplicate_groups: dict[tuple[str, tuple[str, ...]], list[tuple[RecordEntry, RecordTemplate]]] = defaultdict(list)

    for record, template in rows:
        values = record.values or {}
        key = template.key
        # Duplicate candidates require a meaningful identifier or transaction fingerprint.
        reference = next((values.get(k) for k in ("reference", "invoice_number", "receipt_number", "transaction_id") if _normal(values.get(k))), None)
        if reference:
            duplicate_groups[(key, ("reference", _normal(reference)))].append((record, template))
        else:
            date_value = values.get("date") or values.get("order_date") or values.get("payment_date")
            party = values.get("supplier") or values.get("customer") or values.get("party_name")
            amount = next((values.get(k) for k in ("amount", "gross_amount", "expected_amount", "paid_amount", "refund_amount") if values.get(k) is not None), None)
            item = values.get("item") or values.get("product") or values.get("sku")
            fingerprint = (_normal(date_value), _normal(party), _normal(amount), _normal(item))
            if any(fingerprint):
                duplicate_groups[(key, fingerprint)].append((record, template))

        # Negative values can be legitimate adjustments in some businesses, so flag for review rather than reject.
        definitions = {field.get("key"): field for field in (template.fields or [])}
        for field_key, value in values.items():
            definition = definitions.get(field_key, {})
            field_type = str(definition.get("type", "")).lower()
            if field_type in {"money", "number"}:
                number = _decimal(value)
                if number is not None and number < 0:
                    issues.append({
                        "type": "negative_value",
                        "severity": "review",
                        "title": "Negative amount or quantity",
                        "message": f"{template.name}: {field_key.replace('_', ' ')} is {value}. Confirm this is an intentional adjustment or refund.",
                        "record_ids": [str(record.id)],
                        "evidence": {"template": template.key, "field": field_key, "value": value},
                    })

        if key == "stock_counts":
            expected = _decimal(values.get("expected_quantity"))
            counted = _decimal(values.get("counted_quantity"))
            if expected is not None and counted is not None and expected != counted:
                issues.append({
                    "type": "stock_variance",
                    "severity": "review",
                    "title": "Stock count variance",
                    "message": f"{values.get('product', 'Product')}: expected {expected}, counted {counted}; variance is {counted - expected}. Check sales, deliveries, returns, waste, and count accuracy.",
                    "record_ids": [str(record.id)],
                    "evidence": {
                        "product": values.get("product"),
                        "expected_quantity": str(expected),
                        "counted_quantity": str(counted),
                        "variance": str(counted - expected),
                        "date": values.get("date"),
                    },
                })

        if key == "supplier_orders" and not _normal(values.get("reference")):
            issues.append({
                "type": "missing_reference",
                "severity": "info",
                "title": "Supplier order has no reference",
                "message": "Add an order or invoice reference if one exists to make duplicate checking and payment matching more reliable.",
                "record_ids": [str(record.id)],
                "evidence": {"supplier": values.get("supplier"), "order_date": values.get("order_date"), "expected_amount": values.get("expected_amount")},
            })

    for (template_key, fingerprint), group in duplicate_groups.items():
        if len(group) < 2:
            continue
        ids = [str(record.id) for record, _ in group]
        template = group[0][1]
        reference_match = fingerprint[0] == "reference"
        issues.append({
            "type": "possible_duplicate",
            "severity": "review",
            "title": "Possible duplicate records",
            "message": f"{len(group)} records in {template.name} share the same {'reference' if reference_match else 'date, party, amount, and item details'}. Confirm whether they represent separate transactions.",
            "record_ids": ids,
            "evidence": {"template": template_key, "matching_fields": list(fingerprint)},
        })

    issues.sort(key=lambda issue: ({"review": 0, "info": 1}.get(issue["severity"], 2), issue["type"], issue["title"]))
    return {
        "business_id": str(business.id),
        "business_name": business.name,
        "issues": issues,
        "summary": {
            "total": len(issues),
            "needs_review": sum(issue["severity"] == "review" for issue in issues),
            "informational": sum(issue["severity"] == "info" for issue in issues),
        },
        "notice": "These are deterministic review flags, not proof of fraud or theft. Confirm each issue against source documents before taking action.",
    }
