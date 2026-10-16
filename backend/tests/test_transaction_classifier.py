import pytest

from app.services.transaction_classifier import classify_extraction, classify_transaction


@pytest.mark.parametrize(
    ("note", "expected"),
    [
        ("Customer Mike paid 20,000 by transfer for catering", "sale"),
        ("Mike paid me 20,000", "sale"),
        ("Received 20,000 from Mike for catering", "sale"),
        ("Bought gas 8,000", "expense"),
        ("Bought 5 bags of rice from Chidi for 150,000, will pay next week", "supplier_invoice"),
        ("Paid Chidi 50,000 for the rice", "supplier_payment"),
        ("Hello how are you", "none"),
    ],
)
def test_requested_notes_have_expected_fallback_classification(note: str, expected: str) -> None:
    assert classify_transaction(note, None) == expected


def test_ai_classification_takes_priority_over_phrase_fallback() -> None:
    assert classify_transaction("Customer Mike paid 20,000", "expense") == "expense"
    assert classify_transaction("Bought gas 8,000", "sale") == "sale"


def test_unclear_ai_result_uses_fallback_only_as_backup() -> None:
    assert classify_transaction("Mike paid me 20,000", "unclear") == "sale"
    assert classify_transaction("Hello how are you", "unclear") == "none"


def test_existing_ai_invoice_fields_are_used_when_record_type_is_missing() -> None:
    extraction = {"transaction_type": "invoice", "direction": "business_owes_party"}
    result = classify_extraction("Frank invoice 50000", extraction)
    assert result["record_type"] == "supplier_invoice"


def test_ai_record_type_has_precedence_over_phrase_fallback() -> None:
    extraction = {"record_type": "expense", "transaction_type": "payment", "direction": "party_owes_business"}
    assert classify_extraction("Customer Mike paid 20000", extraction)["record_type"] == "expense"
