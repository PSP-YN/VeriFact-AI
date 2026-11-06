import asyncio
import pytest

from app.verify import extract_atomic_claims, parse_atomic_claims


def test_parse_atomic_claims_json():
    claims = parse_atomic_claims('{"claims":["The API is v2.","The price is $5."]}')
    assert claims == ["The API is v2.", "The price is $5."]


def test_parse_atomic_claims_deduplicates_and_limits():
    claims = parse_atomic_claims('{"claims":["A","A","B"]}')
    assert claims == ["A", "B"]
    with pytest.raises(ValueError):
        parse_atomic_claims('{"claims":[' + ",".join('"c%d"' % i for i in range(13)) + ']}')


def test_atomic_claim_extraction_uses_sentence_fallback_without_gateway(monkeypatch):
    monkeypatch.delenv("BIFROST_BASE_URL", raising=False)
    monkeypatch.delenv("BIFROST_MODEL", raising=False)
    claims, method = asyncio.run(extract_atomic_claims("The API is v2. Pricing is $5."))
    assert claims == ["The API is v2.", "Pricing is $5."]
    assert method == "sentence_split"
