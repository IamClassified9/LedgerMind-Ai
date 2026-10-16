"""Shared transaction classification for LedgerMind AI note interpretation.

The model's validated classification is authoritative. Conservative phrase rules are
used only when the model omits or marks the classification unclear.
"""
from __future__ import annotations

import re
from typing import Any

RECORD_TYPES = {"sale", "expense", "supplier_invoice", "supplier_payment", "none", "unclear"}


def _fallback(note: str) -> str:
    text = " ".join((note or "").lower().split())
    if not text:
        return "unclear"
    if re.search(r"\b(hello|hi|how are you|good morning|good afternoon|good evening)\b", text) and not re.search(r"\b(₦|ngn|naira|\d+|paid|bought|sold|received|invoice|expense)\b", text):
        return "none"
    if (re.search(r"\b(paid|sent|transferred)\b", text) and re.search(r"\b(to|supplier|vendor)\b", text)) or re.search(r"\bpaid\s+[a-z][a-z -]{1,40}\s+\d[\d,.]*\s+for\s+(the\s+)?(rice|goods|stock|supplies)\b", text):
        return "supplier_payment"
    if re.search(r"\b(bought|purchase|purchased|invoice|will pay|pay next week|owing|owe)\b", text) and re.search(r"\b(from|supplier|vendor|will pay|pay next week|owing|owe)\b", text):
        return "supplier_invoice"
    if re.search(r"\b(sold|sale|sales|customer|received|collected|paid me|for catering|for food)\b", text):
        return "sale"
    if re.search(r"\b(bought|purchase|purchased|spent|expense|fuel|gas|supplies|cost)\b", text):
        return "expense"
    if re.search(r"\b(paid|payment|transferred|received|bought|sold|invoice)\b", text):
        return "unclear"
    return "none"


def classify_transaction(note: str, ai_record_type: Any = None) -> str:
    """Return a validated type, preferring the AI's decision over phrase fallback."""
    value = str(ai_record_type or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"supplierinvoice": "supplier_invoice", "supplierpayment": "supplier_payment", "non_transaction": "none", "not_a_record": "none"}
    value = aliases.get(value, value)
    if value in RECORD_TYPES and value not in {"unclear"}:
        return value
    return _fallback(note)


def classify_extraction(note: str, extraction: dict[str, Any]) -> dict[str, Any]:
    """Attach the shared classification to a validated AI extraction result."""
    model_type = extraction.get("record_type")
    if model_type in RECORD_TYPES and model_type != "unclear":
        extraction["record_type"] = model_type
        return extraction

    # Existing extraction fields remain useful AI evidence if the new field is absent.
    transaction_type = str(extraction.get("transaction_type") or "").lower()
    direction = str(extraction.get("direction") or "").lower()
    if transaction_type == "invoice" and direction == "business_owes_party":
        extraction["record_type"] = "supplier_invoice"
    elif transaction_type == "payment" and direction == "business_owes_party":
        extraction["record_type"] = "supplier_payment"
    elif transaction_type == "payment" and direction == "party_owes_business":
        extraction["record_type"] = "sale"
    else:
        extraction["record_type"] = classify_transaction(note, model_type)
    return extraction
