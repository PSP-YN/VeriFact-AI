#!/usr/bin/env python3
"""Evaluate VeriFact outputs against a human-labeled JSON dataset."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.evaluation import evaluate_verdicts


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError(f"{path} must contain a JSON array of objects")
    return data


def unique_by_id(records: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result = {}
    for record in records:
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(f"{label} record is missing a non-empty string id")
        if record_id in result:
            raise ValueError(f"Duplicate {label} id: {record_id}")
        result[record_id] = record
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path, help="Human-labeled JSON dataset")
    parser.add_argument("--predictions", required=True, type=Path, help="VeriFact predictions JSON")
    args = parser.parse_args()

    dataset = unique_by_id(load_records(args.dataset), "dataset")
    predictions = unique_by_id(load_records(args.predictions), "prediction")
    if set(dataset) != set(predictions):
        missing = sorted(set(dataset) - set(predictions))
        extra = sorted(set(predictions) - set(dataset))
        raise ValueError(f"IDs must match. Missing predictions={missing}; extra predictions={extra}")

    ids = sorted(dataset)
    expected = [dataset[item]["expected_verdict"] for item in ids]
    predicted = [predictions[item]["verdict"] for item in ids]
    expected_freshness = [dataset[item].get("expected_freshness_score") for item in ids]
    predicted_freshness = [predictions[item].get("freshness_score") for item in ids]

    report = evaluate_verdicts(
        expected,
        predicted,
        expected_freshness=expected_freshness,
        predicted_freshness=predicted_freshness,
    )
    report["dataset_ids"] = ids
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
