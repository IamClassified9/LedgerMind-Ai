"""Gemma narrative analysis over application-calculated business report data.

This module never accepts or executes model-generated SQL. The caller supplies a
server-calculated report snapshot scoped to one authorized business.
"""
import json
import logging
import time
import urllib.error
import urllib.request
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


_TRANSIENT_GEMMA_HTTP_STATUSES = {500, 502, 503, 504}

def _urlopen_with_retries(request: urllib.request.Request, *, timeout: int, api_key: str, operation: str):
    """Retry transient upstream 5xx errors twice, with bounded exponential backoff."""
    for attempt in range(3):
        try:
            return urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            try:
                response_excerpt = exc.read(1200).decode("utf-8", errors="replace")
            except Exception:
                response_excerpt = "<response body unavailable>"
            if api_key:
                response_excerpt = response_excerpt.replace(api_key, "[REDACTED]")
            if exc.code in _TRANSIENT_GEMMA_HTTP_STATUSES and attempt < 2:
                delay = 2 ** attempt
                logger.warning(
                    "%s received transient Gemma HTTP %s; retry %s/2 in %ss",
                    operation, exc.code, attempt + 1, delay,
                )
                time.sleep(delay)
                continue
            logger.error(
                "%s Gemma HTTP failure: status=%s reason=%s response=%r",
                operation, exc.code, exc.reason, response_excerpt[:1200],
            )
            raise



def analyze_business_question(question: str, report: dict[str, Any]) -> str:
    settings = get_settings()
    if not settings.gemma_api_key:
        raise RuntimeError("Gemma is not configured. Set GEMMA_API_KEY in the backend environment.")

    # Pass only aggregated, calculated report fields; never record IDs or raw SQL.
    safe_report = {
        key: report.get(key)
        for key in (
            "business_name", "business_type", "currency", "period", "start_date",
            "end_date", "totals", "counts", "sales_by_payment_method",
            "expenses_by_category", "daily_breakdown", "comparison_to_previous_period",
            "reconciliation", "accounting_note", "supplier_invoice_summary",
        )
        if key in report
    }
    prompt = f"""You are LedgerMind AI, a careful small-business analyst.
Answer the user's question using ONLY the calculated report snapshot below.
Do not invent numbers, transactions, trends, causes, profit, or fraud allegations.
If a requested metric is absent, say it is not available in this report.
Distinguish revenue, operating expenses, purchases, payments, and supplier liabilities.
Explain comparisons only when the snapshot contains the necessary comparison.
Use readable headings and concise bullet points. Clearly state the reporting dates.
The snapshot is application-calculated; do not claim you queried the database directly.

USER QUESTION:
{question}

CALCULATED REPORT SNAPSHOT (JSON):
{json.dumps(safe_report, ensure_ascii=False, default=str)}
"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2500},
    }
    url = (
        f"{settings.gemma_api_base.rstrip('/')}/models/{settings.gemma_model}:generateContent"
        f"?key={settings.gemma_api_key}"
    )
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with _urlopen_with_retries(request, timeout=75, api_key=settings.gemma_api_key, operation="Gemma business analysis") as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        logger.error("Gemma business analysis request failed after retry policy: status=%s", exc.code)
        raise RuntimeError(f"Gemma provider returned HTTP {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        logger.error("Gemma business analysis connection failure: %s", type(exc).__name__)
        raise RuntimeError("Could not reach the Gemma inference provider for business analysis.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemma returned an invalid business analysis response.") from exc

    candidates = body.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemma returned no business analysis response.")
    candidate = candidates[0]
    if candidate.get("finishReason") == "MAX_TOKENS":
        raise RuntimeError("Gemma reached its output token limit while writing the analysis.")
    parts = candidate.get("content", {}).get("parts", [])
    answer = "\n".join(
        part["text"] for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
        and not part.get("thought", False)
    ).strip()
    if not answer:
        raise RuntimeError("Gemma returned no usable business analysis text.")
    return answer
