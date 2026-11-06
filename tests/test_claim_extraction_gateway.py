import asyncio

from app.verify import extract_atomic_claims


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "choices": [
                {"message": {"content": '{"claims":["The current API is v4.","Pricing is $8 per month."]}'}}
            ]
        }


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, *args, **kwargs):
        return FakeResponse()


def test_bifrost_claim_extraction_returns_atomic_claims(monkeypatch):
    monkeypatch.setenv("BIFROST_BASE_URL", "http://bifrost.local")
    monkeypatch.setenv("BIFROST_MODEL", "test/model")
    monkeypatch.setattr("app.verify.httpx.AsyncClient", FakeAsyncClient)

    claims, method = asyncio.run(extract_atomic_claims("The current API is v4 and pricing is $8 per month."))
    assert claims == ["The current API is v4.", "Pricing is $8 per month."]
    assert method == "bifrost_atomic"
