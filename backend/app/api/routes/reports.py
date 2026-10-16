from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import RecordTemplate
from app.models.record_entry import RecordEntry
from app.models.supplier_invoice import SupplierInvoice
from app.models.user import User
from app.security.auth import get_current_user, require_business_access

router = APIRouter()


def _period_dates(
    period: str,
    today: date,
    start_date: date | None,
    end_date: date | None,
) -> tuple[date, date, str]:
    if (start_date is None) != (end_date is None):
        raise HTTPException(status_code=422, detail="Provide both start_date and end_date for a custom range.")
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise HTTPException(status_code=422, detail="start_date must be on or before end_date.")
        return start_date, end_date, "custom"

    if period == "custom":
        raise HTTPException(status_code=422, detail="The custom period requires start_date and end_date.")
    if period == "daily":
        return today, today, period
    if period == "weekly":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6), period
    if period == "monthly":
        start = today.replace(day=1)
        next_month = date(today.year + (today.month == 12), 1 if today.month == 12 else today.month + 1, 1)
        return start, next_month - timedelta(days=1), period
    if period == "yearly":
        return date(today.year, 1, 1), date(today.year, 12, 31), period
    raise HTTPException(status_code=422, detail="period must be daily, weekly, monthly, yearly, or custom.")


def _money(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        return Decimal("0")
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else Decimal("0")
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _serialize_decimal(value: Decimal) -> int | float:
    normalized = value.normalize()
    if normalized == normalized.to_integral_value():
        return int(normalized)
    return float(normalized)


@router.get(
    "/businesses/{business_id}/reports/summary",
    tags=["reports"],
    summary="Summarize a business over a reporting period",
)
def report_summary(
    business_id: UUID,
    period: str = Query(default="monthly", description="daily, weekly, monthly, yearly, or custom"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    business = require_business_access(db, user, business_id)

    try:
        business_today = date.today()  # replaced below with business-local date
        business_today = __import__("datetime").datetime.now(ZoneInfo(business.timezone)).date()
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=422, detail="Business has an invalid timezone configuration.")

    start, end, resolved_period = _period_dates(period, business_today, start_date, end_date)
    statement = (
        select(RecordEntry, RecordTemplate)
        .join(RecordTemplate, RecordEntry.template_id == RecordTemplate.id)
        .where(
            RecordEntry.business_id == business_id,
            RecordTemplate.business_id == business_id,
        )
        .order_by(RecordEntry.created_at.asc(), RecordEntry.id.asc())
    )
    joined = db.execute(statement).all()

    totals: dict[str, Decimal] = defaultdict(Decimal)
    counts: dict[str, int] = defaultdict(int)
    by_day: dict[str, dict[str, Decimal | int]] = {}
    sales_by_method: dict[str, Decimal] = defaultdict(Decimal)
    expenses_by_category: dict[str, Decimal] = defaultdict(Decimal)
    records_in_period = 0
    dated_records = 0
    undated_records = 0
    included_record_ids: list[str] = []

    for record, template in joined:
        values = record.values or {}
        raw_date = values.get("date")
        if not raw_date:
            # Some templates (for example supermarket product catalogue) are
            # reference data rather than dated transactions.
            undated_records += 1
            continue
        try:
            record_date = date.fromisoformat(str(raw_date))
        except ValueError:
            undated_records += 1
            continue
        dated_records += 1
        if not start <= record_date <= end:
            continue

        key = template.key
        amount = Decimal("0")
        category = None
        if key == "daily_sales":
            amount = _money(values.get("gross_amount"))
            totals["sales_revenue"] += amount
            counts["sales_records"] += 1
            sales_by_method[str(values.get("payment_method", "unspecified"))] += amount
        elif key == "sales":
            amount = _money(values.get("amount"))
            totals["sales_revenue"] += amount
            counts["sales_records"] += 1
            sales_by_method[str(values.get("payment_method", "unspecified"))] += amount
        elif key == "expenses":
            amount = _money(values.get("amount"))
            totals["operating_expenses"] += amount
            counts["expense_records"] += 1
            category = str(values.get("category", "uncategorized"))
            expenses_by_category[category] += amount
        elif key == "purchases":
            amount = _money(values.get("amount"))
            totals["purchases"] += amount
            counts["purchase_records"] += 1
        elif key == "payments":
            amount = _money(values.get("amount"))
            direction = values.get("direction")
            if direction == "incoming":
                totals["recorded_incoming_payments"] += amount
                counts["incoming_payment_records"] += 1
            elif direction == "outgoing":
                totals["recorded_outgoing_payments"] += amount
                counts["outgoing_payment_records"] += 1
        elif key == "supplier_payments":
            amount = _money(values.get("amount", values.get("paid_amount")))
            totals["recorded_outgoing_payments"] += amount
            counts["outgoing_payment_records"] += 1
        elif key == "returns":
            amount = _money(values.get("amount", values.get("refund_amount")))
            totals["recorded_returns"] += amount
            counts["return_records"] += 1

        records_in_period += 1
        included_record_ids.append(str(record.id))
        day_key = record_date.isoformat()
        day = by_day.setdefault(day_key, {"sales_revenue": Decimal("0"), "operating_expenses": Decimal("0"), "record_count": 0})
        if key in ("daily_sales", "sales"):
            day["sales_revenue"] = day["sales_revenue"] + amount
        elif key == "expenses":
            day["operating_expenses"] = day["operating_expenses"] + amount
        day["record_count"] = int(day["record_count"]) + 1

    supplier_invoices = list(db.scalars(
        select(SupplierInvoice).where(
            SupplierInvoice.business_id == business_id,
            SupplierInvoice.transaction_date >= start,
            SupplierInvoice.transaction_date <= end,
        )
    ).all())
    supplier_invoice_total = sum((invoice.invoice_amount for invoice in supplier_invoices), Decimal("0"))
    supplier_invoice_paid = sum((invoice.amount_paid for invoice in supplier_invoices), Decimal("0"))
    supplier_invoice_outstanding = sum((invoice.outstanding_amount for invoice in supplier_invoices), Decimal("0"))

    sales = totals["sales_revenue"]
    incoming = totals["recorded_incoming_payments"]
    report_totals = {key: _serialize_decimal(value) for key, value in sorted(totals.items())}
    report_totals.setdefault("sales_revenue", 0)
    report_totals.setdefault("operating_expenses", 0)
    report_totals.setdefault("purchases", 0)
    report_totals.setdefault("recorded_incoming_payments", 0)
    report_totals.setdefault("recorded_outgoing_payments", 0)

    # This is a comparison of separately entered totals, not proof of a shortage:
    # payment records may represent settlements from another period or include
    # non-sales cash movements.
    reconciliation = {
        "sales_minus_incoming_payments": _serialize_decimal(sales - incoming),
        "status": "matches" if sales == incoming else "difference",
        "interpretation": (
            "Recorded sales equal recorded incoming payments for this period."
            if sales == incoming
            else "Recorded sales and incoming payments differ. Review transaction timing, unpaid sales, and non-sales receipts before interpreting this as a discrepancy."
        ),
        "warning": "This comparison is only meaningful when sales and incoming-payment entries cover the same transactions and period.",
    }

    # Compare calendar-based periods to the immediately preceding calendar
    # period. Custom ranges compare against a preceding range of equal length.
    if resolved_period == "daily":
        previous_start = start - timedelta(days=1)
        previous_end = previous_start
    elif resolved_period == "weekly":
        previous_start = start - timedelta(days=7)
        previous_end = start - timedelta(days=1)
    elif resolved_period == "monthly":
        previous_end = start - timedelta(days=1)
        previous_start = previous_end.replace(day=1)
    elif resolved_period == "yearly":
        previous_start = date(start.year - 1, 1, 1)
        previous_end = date(start.year - 1, 12, 31)
    else:
        duration = end - start + timedelta(days=1)
        previous_end = start - timedelta(days=1)
        previous_start = previous_end - duration + timedelta(days=1)
    previous_rows = db.execute(
        select(RecordEntry.values, RecordTemplate.key)
        .join(RecordTemplate, RecordEntry.template_id == RecordTemplate.id)
        .where(RecordEntry.business_id == business_id, RecordTemplate.business_id == business_id)
    ).all()
    previous_sales = Decimal("0")
    previous_expenses = Decimal("0")
    for values, key in previous_rows:
        try:
            record_date = date.fromisoformat(str((values or {}).get("date", "")))
        except ValueError:
            continue
        if previous_start <= record_date <= previous_end:
            if key == "daily_sales":
                previous_sales += _money((values or {}).get("gross_amount"))
            elif key == "sales":
                previous_sales += _money((values or {}).get("amount"))
            elif key == "expenses":
                previous_expenses += _money((values or {}).get("amount"))

    previous = {
        "start_date": previous_start.isoformat(),
        "end_date": previous_end.isoformat(),
        "sales_revenue": _serialize_decimal(previous_sales),
        "operating_expenses": _serialize_decimal(previous_expenses),
    }
    current_sales = sales
    sales_change = None if previous_sales == 0 else _serialize_decimal((current_sales - previous_sales) / previous_sales * Decimal("100"))

    return {
        "business_id": str(business.id),
        "business_name": business.name,
        "business_type": business.business_type,
        "currency": business.currency,
        "period": resolved_period,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": business.timezone,
        "totals": report_totals,
        "counts": dict(sorted(counts.items())),
        "supplier_invoice_summary": {
            "invoice_count": len(supplier_invoices),
            "invoice_total": _serialize_decimal(supplier_invoice_total),
            "amount_paid": _serialize_decimal(supplier_invoice_paid),
            "outstanding_balance": _serialize_decimal(supplier_invoice_outstanding),
        },
        "sales_by_payment_method": {key: _serialize_decimal(value) for key, value in sorted(sales_by_method.items())},
        "expenses_by_category": {key: _serialize_decimal(value) for key, value in sorted(expenses_by_category.items())},
        "daily_breakdown": [
            {
                "date": day,
                "sales_revenue": _serialize_decimal(values["sales_revenue"]),
                "operating_expenses": _serialize_decimal(values["operating_expenses"]),
                "record_count": values["record_count"],
            }
            for day, values in sorted(by_day.items())
        ],
        "comparison_to_previous_period": {
            **previous,
            "sales_revenue_change_percent": sales_change,
        },
        "reconciliation": reconciliation,
        "data_quality": {
            "records_in_period": records_in_period,
            "dated_records_examined": dated_records,
            "undated_or_invalid_date_records_skipped": undated_records,
            "included_record_ids": included_record_ids,
        },
        "accounting_note": "Purchases, cash payments, and operating expenses are shown separately. This summary is not net profit, audited accounts, or proof of theft.",
    }
