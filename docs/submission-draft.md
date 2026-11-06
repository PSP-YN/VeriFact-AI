# VeriFact AI — Hackathon submission draft

> **DRAFT ONLY — not submitted.** Requires project owner review, live integration verification, and final approval.

## Track and problem statement

- Track: Tavily Track
- Problem statement: Build a Stale-Answer Detector for AI Applications

## Project summary

VeriFact AI is a claim-level freshness verification layer for AI-generated answers. It decomposes an answer into independently reviewable claims, retrieves live evidence through Tavily, and uses Bifrost to assess whether the evidence supports, contradicts, or suggests the claim may be stale.

## Problem

AI-generated answers can contain facts that were once correct but are now outdated, especially for software versions, pricing, regulations, product availability, and organizational information.

## Solution

VeriFact AI combines Bifrost-based claim decomposition and evidence assessment with Tavily live research. It returns claim-level verdicts, source URLs, snippets, publication dates when available, retrieval timestamps, freshness scores, and confidence estimates.

## Implemented prototype capabilities

- Bifrost atomic claim extraction with sentence-splitting fallback
- Tavily Search API evidence retrieval
- Per-claim source URL, snippet, relevance score, publication date, retrieval timestamp, and conservative source-provenance hint
- Bifrost evidence assessment
- Supported / contradicted / potentially stale / inconclusive verdicts
- Model-assessed freshness and confidence values with explicit uncalibrated status
- 12-claim request limit to constrain API usage
- HTTP(S)-only evidence links
- Evaluation harness for accuracy, macro-F1, coverage, and freshness MAE
- Browser dashboard and FastAPI endpoint

## Technology and AI usage

- Python / FastAPI
- Tavily Search API
- Bifrost gateway and configured model providers
- HTTPX / Pydantic
- Pytest / GitHub Actions
- HTML/CSS/JavaScript dashboard

AI is used for claim extraction and evidence assessment. Tavily is used for live evidence retrieval. Metrics are computed by deterministic evaluation code when human-labeled ground truth is available.

## Repository

https://github.com/PSP-YN/VeriFact-AI

## Hosted preview

https://veri-fact-ai.vercel.app (public production dashboard; verify judge access in a clean session)

## Demo

See [demo-script.md](demo-script.md) and the official Node.js EOL source-backed stale-claim example.

## Known limitations to disclose

- Freshness and confidence scores are uncalibrated
- Verdict quality has not yet been measured on a sufficiently large human-labeled dataset
- Source credibility ranking and source diversity are not fully implemented
- Claim splitting falls back to sentence/line boundaries if Bifrost extraction fails
- No persistent verification history yet
- External integration requires Tavily API and Bifrost credentials

## Submission checklist

- [ ] Configure Tavily API key and a reachable Bifrost gateway/model
- [ ] Run the Node.js EOL demo with live evidence
- [ ] Build a reviewed, source-backed evaluation set
- [ ] Report accuracy/F1/coverage only from actual evaluation runs
- [ ] Record demo video
- [ ] Finalize pitch deck
- [ ] Owner review and explicit approval
- [ ] Submit only after approval
