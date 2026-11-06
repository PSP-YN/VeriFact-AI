# VeriFact AI demo walkthrough

## Demo claim

Use the UI's **Load example stale claim** button:

> Node.js 18 is currently supported and receives security updates.

This is intentionally outdated. The official Node.js End-of-Life table lists Node.js 18 as EOL; its last listed update was March 27, 2025, and its EOL date is April 30, 2025. EOL releases no longer receive project security fixes.

Source: https://nodejs.org/en/about/eol

The demo is a retrieval-and-assessment example, not a precomputed answer. The actual verdict should be based on live Tavily results and the selected Bifrost model.

## Live demo steps

1. Open the production dashboard: https://veri-fact-ai.vercel.app/ui/
2. Confirm the health indicator shows Tavily configured and Bifrost configured. If either is unavailable, do not present verification as working; use the setup checklist first.
3. Load the example claim.
4. Click **Verify claims**.
5. Show the claim extraction method and per-claim assessment.
6. Open the official Node.js source link returned by Tavily.
7. Explain the difference between:
   - claim verdict (supported / contradicted / potentially stale / inconclusive)
   - freshness score (uncalibrated model assessment)
   - source publication date (may be absent)
   - retrieval timestamp (when VeriFact queried Tavily)

## Judge-facing caveat

A correct retrieval does not automatically guarantee a correct LLM verdict. The current freshness and confidence scores are uncalibrated. The team will report accuracy, macro-F1, coverage, and freshness-score MAE only after evaluating against human-labeled, source-backed cases.
