# VeriFact evaluation dataset

This directory is for **human-labeled, source-backed evaluation records**. `dataset.example.json` contains one real Node.js EOL example for exercising the evaluation pipeline; it is not a sufficiently large benchmark and must not be used to claim model accuracy.

## Dataset record format

Each record should contain:

- `id`: stable unique identifier
- `claim`: the claim under test
- `as_of`: timestamp at which the claim is evaluated
- `expected_verdict`: one of `supported`, `contradicted`, `potentially_stale`, or `inconclusive`
- `source_urls`: one or more sources used by the human labeler
- `expected_freshness_score`: optional human rubric score from 0 to 100

The prediction file uses the same `id` and includes VeriFact's `verdict` and optional `freshness_score`.

Example shape (schema only; replace placeholders with reviewed data):

```json
[
  {
    "id": "reviewed-claim-001",
    "claim": "Claim text reviewed by the team",
    "as_of": "2026-11-06T12:00:00Z",
    "expected_verdict": "inconclusive",
    "source_urls": ["https://example.org/source"],
    "expected_freshness_score": null
  }
]
```

The example is a template, not a labeled benchmark case.

## Run evaluation

```bash
python scripts/evaluate_verdicts.py --dataset evaluation/dataset.json --predictions evaluation/predictions.json
```

The report includes:

- Accuracy
- Macro F1
- Coverage (share of predictions not labeled inconclusive)
- Confusion matrix and per-class precision/recall/F1
- Freshness-score MAE where both human and model scores exist

## Labeling guidelines

1. Record the evaluation `as_of` time.
2. Prefer primary/official sources and preserve the source URL.
3. Distinguish a claim that is false from one that was once true but is stale.
4. Use `inconclusive` when evidence is insufficient or conflicting.
5. Keep expected freshness score human-rubric-based and clearly documented.
6. Do not report model accuracy until the dataset has been reviewed, held-out, and run through this script.
