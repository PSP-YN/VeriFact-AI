from pathlib import Path
import os

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.verify import extract_atomic_claims, initial_temporal_label, search_evidence
from app.verifier import BifrostVerificationError, assess_claim

MAX_CLAIMS_PER_REQUEST = 12

app = FastAPI(
    title="VeriFact AI",
    version="0.1.0",
    description="Claim-level freshness and evidence retrieval for AI answers",
)


class VerifyRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=20000)
    max_results_per_claim: int = Field(default=5, ge=1, le=10)


@app.get("/")
def root():
    return RedirectResponse(url="/ui/")


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
    claims, claim_extraction_method = await extract_atomic_claims(request.answer)
    if not claims:
        raise HTTPException(status_code=422, detail="No verifiable claims found in answer")
    if len(claims) > MAX_CLAIMS_PER_REQUEST:
        raise HTTPException(
            status_code=413,
            detail=f"Answer split into {len(claims)} claims. Limit is {MAX_CLAIMS_PER_REQUEST} per request; shorten or split the answer.",
        )

    results = []
    assessed_count = 0
    for index, claim in enumerate(claims, start=1):
        try:
            evidence = await search_evidence(claim, request.max_results_per_claim)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Evidence search failed: {type(exc).__name__}") from exc

        assessment_failed = False
        try:
            assessment = await assess_claim(claim, evidence)
        except BifrostVerificationError as exc:
            assessment_failed = True
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
        elif not assessment_failed:
            assessed_count += 1

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
        "claim_extraction_method": claim_extraction_method,
        "verification_status": "model_assessed" if assessed_count else "evidence_only",
        "assessed_claim_count": assessed_count,
        "assessment_warning": "LLM verdicts and freshness scores are uncalibrated model assessments, not guarantees.",
    }


app.mount(
    "/ui",
    StaticFiles(directory=Path(__file__).resolve().parent.parent / "static", html=True),
    name="ui",
)
