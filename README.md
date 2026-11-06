# VeriFact AI

A claim-level freshness and verification layer for AI-generated answers. It identifies potentially time-sensitive claims, retrieves current evidence with Tavily, and uses Bifrost to assess evidence when configured.

> Hackathon MVP in active development. Verdicts and model-generated freshness/confidence scores are uncalibrated assessments, not truth guarantees.

## Live deployment

- **Dashboard:** https://veri-fact-ai.vercel.app/ui/
- **Health:** https://veri-fact-ai.vercel.app/health
- **API docs:** https://veri-fact-ai.vercel.app/docs
- **OpenAPI:** https://veri-fact-ai.vercel.app/openapi.json

The deployment responds, but external provider credentials must be configured in Vercel before live claim verification can work. Check the health response for `tavily_configured` and `bifrost_configured`; both should be `true` for the full demo.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the verification pipeline and evaluation flow.

## Current implementation

- FastAPI backend and browser dashboard
- Bifrost-based atomic claim extraction with sentence/line fallback
- Tavily Search API evidence retrieval
- Source title, URL, snippet, relevance score, publication date, retrieval timestamp, and conservative source-provenance hint
- Temporal-sensitivity heuristic
- Bifrost OpenAI-compatible model assessment
- Evidence-only fallback when Bifrost is not configured
- Validation of verdict and score fields
- Human-labeled evaluation metrics (accuracy, macro-F1, coverage, freshness MAE)
- Request cap of 12 claims to control external API usage
- HTTP(S)-only source-link validation
- Baseline security headers and `no-store` for API responses
- Pytest and GitHub Actions CI

## Quick start

Requirements: Python 3.12+, a Tavily API key, and optionally a Bifrost gateway/model.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your Tavily key; configure Bifrost if desired.
uvicorn app.main:app --reload --env-file .env
```

Open http://localhost:8000 for the dashboard and http://localhost:8000/docs for API docs.

## Tests

Run the automated test suite locally:

```bash
pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests to `main`.

## Environment

```env
TAVILY_API_KEY=your_tavily_key
BIFROST_BASE_URL=http://localhost:8080
BIFROST_API_KEY=your_bifrost_virtual_key_if_required
BIFROST_MODEL=provider/model-route
```

Keep actual keys in your local `.env`; never commit them.

## API

- `GET /health` — service and configuration status
- `POST /api/v1/verify` — claim extraction, Tavily search, and optional Bifrost assessment

Example:

```json
{
  "answer": "The latest version of Example API is v3. Example pricing is $10/month.",
  "max_results_per_claim": 5
}
```

## Demo

See [`docs/demo-script.md`](docs/demo-script.md) for the official Node.js 18 EOL stale-claim walkthrough and judge-facing explanation.

## Important limitations

- When Bifrost is configured, claim decomposition uses the selected model; without it or on extractor failure, the app falls back to sentence/line splitting.
- Tavily relevance is not proof of claim truth.
- Bifrost assessments and score outputs are not calibrated against a ground-truth dataset yet.
- Source provenance labels are conservative domain heuristics, not proof that a source is authoritative for a particular claim.
- Evidence publication dates may be absent; the system must not silently treat retrieval time as publication time.
- This MVP does not yet implement production-grade distributed rate limiting, durable job processing, or benchmark-backed score calibration.
- The UI displays sources returned for each claim and the assessment status.

## Roadmap

1. Add a curated benchmark of current vs stale claims
2. Improve atomic claim extraction and temporal fact types
3. Implement source authority, contradiction handling and source diversity
4. Calibrate freshness score against ground-truth examples
5. Add distributed rate limits, caching, retries, and multi-claim concurrency
6. Validate end-to-end behavior with live Tavily and Bifrost keys

## Hackathon

Geek Room Global AI Hackathon — Tavily Track: “Build a Stale-Answer Detector for AI Applications.”

## Vercel environment

Set these values in Vercel Project Settings → Environment Variables. Never commit credentials:

- `TAVILY_API_KEY`: Tavily search key.
- `BIFROST_BASE_URL`: reachable gateway URL. **Do not use localhost** for Vercel because it refers to the serverless runtime.
- `BIFROST_API_KEY`: inference key if required by the gateway.
- `BIFROST_MODEL`: configured Bifrost model route.

After setting or changing environment variables, redeploy and confirm `/health` reports both providers configured. Environment values are not shown by health endpoint.

## Privacy

The answer text is sent to the configured Bifrost model for claim extraction when enabled. Extracted claims are sent to Tavily for search, and claim/evidence text is sent to Bifrost for assessment. Avoid submitting confidential or personal information. The app does not persist answer history in a database in this MVP; provider logging follows the configured service policies.
