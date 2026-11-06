from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.evaluation import evaluate_verdicts

client = TestClient(app)


def test_health_endpoint_and_security_headers():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "VeriFact AI"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


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
    assert response.headers["cache-control"] == "no-store"
    payload = response.json()
    assert payload["claim_count"] == 1
    assert payload["claims"][0]["verdict"] == "supported"
    assert payload["claims"][0]["freshness_score"] == 90


def test_verify_rejects_more_than_twelve_claims():
    answer = " ".join(f"Claim {index}." for index in range(13))
    response = client.post("/api/v1/verify", json={"answer": answer})
    assert response.status_code == 413


def test_failed_bifrost_assessment_is_not_counted_as_assessed(monkeypatch):
    async def fake_search(claim, max_results=5):
        return []

    async def failed_assess(claim, evidence):
        from app.verifier import BifrostVerificationError
        raise BifrostVerificationError("simulated bad response")

    monkeypatch.setattr("app.main.search_evidence", fake_search)
    monkeypatch.setattr("app.main.assess_claim", failed_assess)
    response = client.post("/api/v1/verify", json={"answer": "The latest version is v2."})
    assert response.status_code == 200
    payload = response.json()
    assert payload["verification_status"] == "evidence_only"
    assert payload["assessed_claim_count"] == 0
    assert payload["claims"][0]["verdict"] == "inconclusive"


def test_evaluation_metrics_and_freshness_mae():
    metrics = evaluate_verdicts(
        ["supported", "contradicted", "inconclusive"],
        ["supported", "supported", "inconclusive"],
        expected_freshness=[80, None, 40],
        predicted_freshness=[70, 90, 40],
    )
    assert metrics["sample_count"] == 3
    assert metrics["accuracy"] == pytest.approx(2 / 3, abs=0.0001)
    assert metrics["coverage"] == pytest.approx(2 / 3, abs=0.0001)
    # Only the two labeled examples count: absolute errors 10 and 0 => MAE 5.
    assert metrics["freshness_mae"] == 5
    assert metrics["freshness_mae_sample_count"] == 2


def test_evaluation_rejects_mismatched_and_empty_data():
    with pytest.raises(ValueError):
        evaluate_verdicts(["supported"], ["supported", "contradicted"])
    with pytest.raises(ValueError):
        evaluate_verdicts([], [])
