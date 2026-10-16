"""Hosted Gemma inference for LedgerMind record interpretation."""

import json
import logging
import time
import urllib.error
import urllib.request
from typing import Any

from app.core.config import get_settings
from app.services.transaction_classifier import classify_extraction

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


SYSTEM_INSTRUCTION = """Extract facts from the business note.

Return exactly one JSON object. Do not explain your reasoning.
Use only these keys:
transaction_type, record_type, party_name, direction, invoice_amount, amount_paid,
currency, transaction_date, reference, note, missing_information, ambiguity.

transaction_type: invoice, payment, or unknown.
record_type: sale, expense, supplier_invoice, supplier_payment, none, or unclear.
Classify the business event from the note. A customer paying the business is sale; the business buying goods now and owing a supplier is supplier_invoice; the business paying a supplier for an earlier purchase is supplier_payment; other business costs are expense. Greetings or ordinary questions with no transaction are none. If direction or intent cannot be determined, use unclear. Do not infer missing facts.
direction: business_owes_party, party_owes_business, or unknown.
Amounts must be numbers or null.
Unknown string fields must be null.
transaction_date must use YYYY-MM-DD or null.
missing_information and ambiguity must be arrays of strings.

If a supplier invoice explicitly says payment will happen later and gives no payment made, set amount_paid to 0. Do not invent facts, amounts, dates, identity, or payment direction.
A payment note alone does not prove money was received.
Do not claim fraud.
Preserve the original currency symbol and meaning.
This is extraction, not accounting advice."""

REQUIRED_KEYS = {
    "transaction_type", "party_name", "direction", "invoice_amount",
    "amount_paid", "currency", "transaction_date", "reference", "note",
    "missing_information", "ambiguity",
}


def _extract_response_text(body: dict[str, Any]) -> str:
    """Extract answer text while ignoring parts marked as thoughts."""
    candidates = body.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise RuntimeError("Gemma returned no response candidates.")

    candidate = candidates[0]
    finish_reason = candidate.get("finishReason", "unknown")
    parts = candidate.get("content", {}).get("parts", [])
    answer_parts = [
        part["text"] for part in parts
        if isinstance(part, dict)
        and isinstance(part.get("text"), str)
        and not part.get("thought", False)
    ]

    if finish_reason == "MAX_TOKENS":
        logger.warning("Gemma reached the output token limit.")
        raise RuntimeError("Gemma reached its output token limit before completing the response.")
    if not answer_parts:
        raise RuntimeError(
            f"Gemma returned no usable answer text (finish reason: {finish_reason})."
        )
    return "\n".join(answer_parts).strip()


def interpret_business_note(note: str, *, today: str | None = None, timezone_name: str = "UTC", currency: str | None = None) -> dict[str, Any]:
    """Interpret a business note and return validated structured data."""
    settings = get_settings()
    if not settings.gemma_api_key:
        raise RuntimeError(
            "Gemma is not configured. Set GEMMA_API_KEY in the backend environment."
        )
    if not note or not note.strip():
        raise ValueError("The business note cannot be empty.")

    date_context = (
        f"\nAUTHORITATIVE DATE CONTEXT: Today is {today} in timezone {timezone_name}. "
        "Resolve relative dates such as yesterday, today, and last Friday from this date and timezone. "
        "Do not guess the current date. Return the resolved transaction_date in YYYY-MM-DD format.\n"
        if today else ""
    )
    currency_context = (
        f"\nBusiness reporting currency: {currency}. Use this currency when a currency is not explicitly stated; do not convert amounts.\n"
        if currency else ""
    )
    prompt = (
        f"{SYSTEM_INSTRUCTION}{date_context}{currency_context}\n\nBusiness note:\n{note}\n\n"
        "Return the complete JSON object now."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1,
            "maxOutputTokens": 5000,
        },
    }
    url = (
        f"{settings.gemma_api_base.rstrip('/')}"
        f"/models/{settings.gemma_model}:generateContent"
        f"?key={settings.gemma_api_key}"
    )
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        try:
            import sentry_sdk
            span_context = sentry_sdk.start_span(
                op="gen_ai.request",
                description=f"Gemma record interpretation ({settings.gemma_model})",
            )
        except ImportError:
            span_context = None

        if span_context is None:
            with _urlopen_with_retries(request, timeout=75, api_key=settings.gemma_api_key, operation="Gemma record interpretation") as response:
                body = json.loads(response.read().decode("utf-8"))
        else:
            with span_context:
                with _urlopen_with_retries(request, timeout=75, api_key=settings.gemma_api_key, operation="Gemma record interpretation") as response:
                    body = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as exc:
        logger.error("Gemma provider request failed after retry policy: status=%s", exc.code)
        raise RuntimeError(f"Gemma provider returned HTTP {exc.code}.") from exc
    except urllib.error.URLError as exc:
        logger.error(
            "Gemma connection failure: reason_type=%s reason=%s",
            type(exc.reason).__name__, str(exc.reason)[:300],
        )
        raise RuntimeError("Could not reach the Gemma inference provider.") from exc
    except TimeoutError as exc:
        logger.error("Gemma inference request timed out.")
        raise RuntimeError("Gemma inference timed out. The provider took too long to respond.") from exc
    except json.JSONDecodeError as exc:
        logger.error("Gemma returned an invalid provider response body.")
        raise RuntimeError("Gemma returned an invalid provider response.") from exc

    try:
        raw = _extract_response_text(body)
    except RuntimeError as exc:
        logger.warning("Gemma response structure error: %s", exc)
        raise

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning(
            "Gemma JSON parse failure: %s at line %s, column %s. Preview: %r",
            exc.msg, exc.lineno, exc.colno, raw[:1000],
        )
        raise RuntimeError(
            "Gemma returned a response that was not valid structured JSON."
        ) from exc

    if not isinstance(result, dict) or not REQUIRED_KEYS.issubset(result):
        logger.warning(
            "Gemma schema mismatch. Returned keys: %s",
            sorted(result.keys()) if isinstance(result, dict) else type(result).__name__,
        )
        raise RuntimeError("Gemma response did not match the required extraction schema.")

    # Classification is allowed to be absent or unclear; the shared classifier
    # applies the conservative fallback in that case.
    if not isinstance(result.get("record_type"), str) or result.get("record_type") not in {"sale", "expense", "supplier_invoice", "supplier_payment", "none", "unclear"}:
        result["record_type"] = "unclear"

    if result["transaction_type"] not in {"invoice", "payment", "unknown"}:
        raise RuntimeError("Gemma returned an invalid transaction_type.")
    if result["record_type"] not in {"sale", "expense", "supplier_invoice", "supplier_payment", "none", "unclear"}:
        raise RuntimeError("Gemma returned an invalid record_type.")
    if result["direction"] not in {
        "business_owes_party", "party_owes_business", "unknown",
    }:
        raise RuntimeError("Gemma returned an invalid direction.")

    for key in ("invoice_amount", "amount_paid"):
        value = result.get(key)
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0
        ):
            raise RuntimeError(f"Gemma returned an invalid {key} value.")

    for key in ("missing_information", "ambiguity"):
        if not isinstance(result[key], list) or not all(
            isinstance(item, str) for item in result[key]
        ):
            raise RuntimeError(f"Gemma returned an invalid {key} value.")

    return classify_extraction(note, result)
