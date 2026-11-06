import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.verify import extract_claims, initial_temporal_label, search_evidence
from app.verifier import BifrostVerificationError, assess_claim

app = FastAPI(
    title="VeriFact AI",
    version="0.1.0",
    description="Claim-level freshness and evidence retrieval for AI answers",
)


class VerifyRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=20000)
    max_results_per_claim: int = Field(default=5, ge=1, le=10)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "VeriFact AI",
        "version": "0.1.0",
        "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
        "bifrost_configured": bool(os.getenv("BIFROST_BASE_URL") and os.getenv("BIFROST_MODEL")),
    }


@app.post("/api/v1/verify")
async def verify_answer(request: VerifyRequest):
    claims = extract_claims(request.answer)
    if not claims:
        raise HTTPException(status_code=422, detail="No verifiable claims found in answer")

    results = []
    verified_count = 0
    for index, claim in enumerate(claims, start=1):
        try:
            evidence = await search_evidence(claim, request.max_results_per_claim)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Evidence search failed: {type(exc).__name__}") from exc

        try:
            assessment = await assess_claim(claim, evidence)
        except BifrostVerificationError as exc:
            assessment = {
                "verdict": "inconclusive",
                "rationale": f"Verifier unavailable or invalid response: {exc}",
                "freshness_score": None,
                "freshness_score_status": "not_assessed",
                "confidence": None,
                "confidence_status": "not_assessed",
            }

        if assessment is None:
            assessment = {
                "verdict": "inconclusive",
                "rationale": "Bifrost is not configured; evidence was retrieved but not assessed.",
                "freshness_score": None,
                "freshness_score_status": "not_assessed",
                "confidence": None,
                "confidence_status": "not_assessed",
            }
        else:
            verified_count += 1

        results.append({
            "claim_id": f"claim-{index}",
            "claim": claim,
            "temporal_sensitivity": initial_temporal_label(claim),
            **assessment,
            "evidence": evidence,
        })

    return {
        "claims": results,
        "claim_count": len(results),
        "verification_status": "model_assessed" if verified_count else "evidence_only",
        "assessed_claim_count": verified_count,
        "assessment_warning": "LLM verdicts and freshness scores are uncalibrated model assessments, not guarantees.",
    }
