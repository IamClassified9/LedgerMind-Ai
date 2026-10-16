from uuid import UUID

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.ai_assistant import interpret_business_note
from app.services.transaction_classifier import classify_extraction
from app.services.business_analyst import analyze_business_question
from app.api.routes.reports import report_summary
from app.db.session import get_db
from app.models.user import User
from app.models.business import Business
from app.security.auth import require_business_access
from app.services.country_settings import local_today, valid_timezone
from app.security.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI assistance"])


class InterpretRequest(BaseModel):
    note: str = Field(min_length=5, max_length=20000)
    business_id: UUID | None = None


@router.post("/interpret-record")
def interpret_record(payload: InterpretRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    """Extract candidate fields from a note; never writes to accounting records."""
    business = require_business_access(db, user, payload.business_id) if payload.business_id else None
    timezone_name = valid_timezone(business.timezone) if business else "UTC"
    today = local_today(timezone_name)
    try:
        result = interpret_business_note(payload.note.strip(), today=today, timezone_name=timezone_name, currency=business.currency if business else None)
    except RuntimeError as exc:
        message = str(exc)
        status_code = 503 if "not configured" in message or "Could not reach" in message else 502
        raise HTTPException(status_code=status_code, detail=message) from exc
    result = classify_extraction(payload.note.strip(), result)
    return {
        "model": "configured-open-weight-gemma",
        "saved": False,
        "review_required": True,
        "extraction": result,
        "notice": "AI-extracted values are suggestions. Review and confirm them before saving; balances must be calculated by LedgerMind, not the model.",
    }


class BusinessAnalysisRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    period: str | None = Field(default=None, pattern="^(daily|weekly|monthly|yearly)$")


@router.post("/businesses/{business_id}/analysis")
def analyze_business(
    business_id: UUID,
    payload: BusinessAnalysisRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Analyze an application-calculated report snapshot, never model-generated SQL."""
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Please enter a business question.")
    period = payload.period
    if period is None:
        lowered = question.lower()
        if any(term in lowered for term in ("this week", "weekly", "week's", "week of")):
            period = "weekly"
        elif any(term in lowered for term in ("this year", "yearly", "annual", "this year's")):
            period = "yearly"
        elif any(term in lowered for term in ("today", "today's", "daily")):
            period = "daily"
        else:
            period = "monthly"
    try:
        snapshot = report_summary(business_id, period, None, None, db, user)
        snapshot["supplier_invoice_summary"]["note"] = (
            "Supplier invoices are summarized separately from generic purchase records to avoid silently double-counting."
        )
        answer = analyze_business_question(question, snapshot)
    except HTTPException:
        raise
    except RuntimeError as exc:
        message = str(exc)
        status_code = 503 if "not configured" in message or "Could not reach" in message else 502
        raise HTTPException(status_code=status_code, detail=message) from exc
    return {
        "business_id": str(business_id),
        "question": question,
        "period": snapshot["period"],
        "start_date": snapshot["start_date"],
        "end_date": snapshot["end_date"],
        "answer": answer,
        "calculated_data": {
            "totals": snapshot["totals"],
            "counts": snapshot["counts"],
            "expenses_by_category": snapshot["expenses_by_category"],
            "comparison_to_previous_period": snapshot["comparison_to_previous_period"],
            "supplier_invoice_summary": snapshot["supplier_invoice_summary"],
        },
        "notice": "Numbers are calculated from saved records for this business and period. The AI provides narrative interpretation only."
    }
