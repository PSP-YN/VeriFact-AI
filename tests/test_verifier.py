import pytest

from app.verifier import BifrostVerificationError, _parse_json, assess_claim


def test_parse_json_plain():
    assert _parse_json('{"verdict":"supported"}')["verdict"] == "supported"


def test_parse_json_rejects_invalid():
    with pytest.raises(BifrostVerificationError):
        _parse_json("not json")


@pytest.mark.anyio
async def test_assess_claim_returns_none_when_gateway_unconfigured(monkeypatch):
    monkeypatch.delenv("BIFROST_BASE_URL", raising=False)
    monkeypatch.delenv("BIFROST_MODEL", raising=False)
    assert await assess_claim("claim", []) is None
