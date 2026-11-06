# VeriFact AI — Release and Hackathon Submission Checklist

This document is the release gate. Do not describe the project as production-ready until the applicable checks below are verified against the deployed build.

## 1. Code and CI

- [ ] GitHub Actions CI completes successfully on the exact release commit.
- [ ] Run `pytest -q` locally or in CI; retain the test output.
- [ ] Test API validation, malformed input, provider failures, security headers, and claim limit.
- [ ] Confirm no secrets are committed. Rotate any key that was ever exposed in a commit, log, screenshot, or demo recording.
- [ ] Review dependency vulnerabilities and pin/upgrade packages where practical.
- [ ] Confirm all deployment settings are documented and configured in Vercel.
- [ ] Confirm Bifrost endpoint is publicly reachable from Vercel (not localhost).
- [ ] Verify Tavily and Bifrost provider errors degrade to safe, honest responses.

## 2. Deployment smoke test

- [ ] Open the production URL in a clean browser session.
- [ ] `GET /health` returns the expected status without exposing secrets.
- [ ] Dashboard loads without browser-console errors.
- [ ] Submit one ordinary factual claim and inspect claim extraction, citations, verdict, and timestamps.
- [ ] Submit multiple claims; confirm the API enforces the maximum claim count.
- [ ] Test unavailable/invalid provider configuration and confirm the response is not presented as verified truth.
- [ ] Confirm HTTPS, security headers, and no-store API cache policy on deployed responses.
- [ ] Check responsive behavior at desktop and mobile viewport sizes.

## 3. Demo and judge presentation

- [ ] Use the documented live demo claim from `docs/demo-script.md`.
- [ ] Show the source page and explain why Node.js 18 is EOL; avoid implying the model is infallible.
- [ ] Explain the difference between verdict, retrieval relevance, source publication date, and retrieval timestamp.
- [ ] State that freshness/confidence scores are uncalibrated.
- [ ] Do not claim benchmark accuracy, production adoption, or reliability without measured evidence.
- [ ] Record a backup demo only after verifying the live version; label any recorded/offline material accurately.

## 4. Security, privacy, and operational limitations

- [ ] Explain that claim text is sent to configured external model/search providers (Bifrost and Tavily).
- [ ] Do not paste credentials, private documents, or sensitive personal data into the demo.
- [ ] Verify provider/API keys are stored only in environment variables / deployment secrets.
- [ ] Confirm logs do not contain raw secrets or unnecessarily retain user claim text.
- [ ] Note that the current MVP has no durable verification history/database.
- [ ] Note that rate limiting, abuse controls, durable background jobs, calibrated scores, and service-level monitoring are not yet implemented unless subsequently added and tested.

## 5. Submission materials

- [ ] README clearly describes the problem, workflow, architecture, setup, API, and limitations.
- [ ] Repository is public and contains no credentials or private files.
- [ ] Official hackathon submission fields are completed using accurate descriptions.
- [ ] Demo URL and repository URL are accessible to judges.
- [ ] Confirm team/track/eligibility and submission deadline on the official event page.
- [ ] Review the final submission preview and obtain user approval before submitting.

## Release decision

- **Ready for demo:** only after the deployed smoke tests above are completed.
- **Ready for submission:** demo-ready plus submission fields/materials reviewed.
- **Production-ready:** not claimed until security review, abuse/rate controls, observability, calibrated evaluation, reliability testing, and privacy/retention decisions are completed.

Record the release commit SHA, CI run URL, deployment URL, and test date in the final release notes.
