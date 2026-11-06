from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "VeriFact AI"


def test_verify_endpoint_with_mocked_external_services(monkeypatch):
    async def fake_search(claim, max_results=5):
        return [{"title": "Example source", "url": "https://example.org", "snippet": "Evidence text", "retrieved_at": "test"}]

    async def fake_assess(claim, evidence):
        return {
            "verdict": "supported",
            "rationale": "Mocked unit-test assessment",
            "freshness_score": 90,
            "freshness_score_status": "model_assessment_uncalibrated",
            "confidence": 0.8,
            "confidence_status": "model_estimate_uncalibrated",
            "model": "test-model",
        }

    monkeypatch.setattr("app.main.search_evidence", fake_search)
    monkeypatch.setattr("app.main.assess_claim", fake_assess)
    response = client.post("/api/v1/verify", json={"answer": "The latest version is v2."})
    assert response.status_code == 200
    payload = response.json()
    assert payload["claim_count"] == 1
    assert payload["claims"][0]["verdict"] == "supported"
    assert payload["claims"][0]["freshness_score"] == 90
