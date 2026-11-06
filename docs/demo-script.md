# VeriFact AI demo walkthrough

## Demo claim

Use the UI's **Load example stale claim** button:

> Node.js 18 is currently supported and receives security updates.

This is intentionally outdated. The official Node.js EOL page lists Node.js 18 as End-of-Life (last updated March 27, 2025) and explains that EOL versions no longer receive project security updates.

Source: https://nodejs.org/en/about/eol

The demo is a retrieval-and-assessment example, not a precomputed answer. The actual verdict should be based on the live Tavily results and the selected Bifrost model.

## Live demo steps

1. Open the VeriFact dashboard.
2. Load the example claim.
3. Confirm the health indicator shows Tavily configured and Bifrost configured.
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
