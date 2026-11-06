# VeriFact AI

A claim-level freshness and verification layer for AI-generated answers. The system is designed to flag potentially stale claims, retrieve current evidence through Tavily, and present claim-level verdicts with citations.

> Early development — initial scaffold. The app must not invent sources, claim certainty without evidence, or present freshness as a calibrated probability before validation.

## Hackathon

Geek Room Global AI Hackathon — Tavily Track: “Build a Stale-Answer Detector for AI Applications.”

## Planned stack

- Python 3.12+
- FastAPI
- Tavily Search API for live evidence retrieval
- Bifrost gateway for model-provider routing
- Pydantic schemas
- Pytest

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Principles

- Split answers into independently reviewable claims.
- Treat temporal validity separately from general truth.
- Attach source URLs and retrieval timestamps to evidence.
- Distinguish supported, contradicted, inconclusive, and not-checked claims.
- Never store secrets in Git.
- Do not claim the Tavily/Bifrost integration works until credentials and end-to-end tests verify it.

## Roadmap

1. Claim extraction and typed verification response
2. Tavily evidence retrieval
3. Freshness classification and transparent scoring
4. Bifrost model routing
5. Evaluation dataset and test suite
6. Frontend and deployment
