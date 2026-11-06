from app.verify import extract_claims, initial_temporal_label


def test_extract_claims_splits_sentences_and_lines():
    claims = extract_claims("The API is v1. The price is $10\nNext claim")
    assert claims == ["The API is v1.", "The price is $10", "Next claim"]


def test_time_sensitive_claim_is_flagged():
    assert initial_temporal_label("The latest API version is v3") == "time_sensitive"


def test_unknown_temporal_sensitivity_is_not_misrepresented():
    assert initial_temporal_label("Water is composed of hydrogen and oxygen") == "temporal_sensitivity_unknown"


def test_security_support_claim_is_time_sensitive():
    assert initial_temporal_label("Node.js 18 receives security updates") == "time_sensitive"


def test_end_of_life_claim_is_time_sensitive():
    assert initial_temporal_label("Node.js 18 reached end of life") == "time_sensitive"
