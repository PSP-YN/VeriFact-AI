import asyncio
import pytest

from app.verifier import BifrostVerificationError, _parse_json, assess_claim


def test_parse_json_plain():
    assert _parse_json('{"verdict":"supported"}')["verdict"] == "supported"


def test_parse_json_rejects_invalid():
    with pytest.raises(BifrostVerificationError):
        _parse_json("not json")


def test_assess_claim_returns_none_when_gateway_unconfigured(monkeypatch):
    monkeypatch.delenv("BIFROST_BASE_URL", raising=False)
    monkeypatch.delenv("BIFROST_MODEL", raising=False)
    assert asyncio.run(assess_claim("claim", [])) is None


def test_assess_claim_rejects_boolean_freshness_score(monkeypatch):
    import asyncio

    class Response:
        def raise_for_status(self):
            return None
        def json(self):
            return {"choices":[{"message":{"content":'{"verdict":"supported","rationale":"x","freshness_score":true,"confidence":0.5}'}}]}

    class Client:
        def __init__(self,*args,**kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self,*args): return False
        async def post(self,*args,**kwargs): return Response()

    monkeypatch.setenv("BIFROST_BASE_URL","http://bifrost.local")
    monkeypatch.setenv("BIFROST_MODEL","test/model")
    monkeypatch.setattr("app.verifier.httpx.AsyncClient",Client)
    with pytest.raises(BifrostVerificationError):
        asyncio.run(assess_claim("claim",[]))
