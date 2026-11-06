"""Metrics for evaluating VeriFact predictions against human-labeled data."""
from __future__ import annotations

from typing import Any

LABELS = ("supported", "contradicted", "potentially_stale", "inconclusive")


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def evaluate_verdicts(
    expected: list[str],
    predicted: list[str],
    expected_freshness: list[float | None] | None = None,
    predicted_freshness: list[float | None] | None = None,
) -> dict[str, Any]:
    if len(expected) != len(predicted):
        raise ValueError("expected and predicted must have equal lengths")
    if not expected:
        raise ValueError("At least one labeled example is required")
    if any(label not in LABELS for label in expected + predicted):
        raise ValueError(f"Labels must be one of: {', '.join(LABELS)}")

    confusion = {label: {other: 0 for other in LABELS} for label in LABELS}
    for truth, guess in zip(expected, predicted):
        confusion[truth][guess] += 1

    per_class = {}
    f1_values = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in LABELS if other != label)
        fn = sum(confusion[label][other] for other in LABELS if other != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = _f1(precision, recall)
        per_class[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(confusion[label].values()),
        }
        f1_values.append(f1)

    accuracy = sum(truth == guess for truth, guess in zip(expected, predicted)) / len(expected)
    coverage = sum(guess != "inconclusive" for guess in predicted) / len(predicted)

    freshness_mae = None
    if expected_freshness is not None and predicted_freshness is not None:
        if len(expected_freshness) != len(expected) or len(predicted_freshness) != len(expected):
            raise ValueError("Freshness score arrays must align with labels")
        pairs = [
            (float(truth), float(guess))
            for truth, guess in zip(expected_freshness, predicted_freshness)
            if truth is not None and guess is not None
        ]
        if pairs:
            freshness_mae = round(sum(abs(truth - guess) for truth, guess in pairs) / len(pairs), 4)

    return {
        "sample_count": len(expected),
        "accuracy": round(accuracy, 4),
        "macro_f1": round(sum(f1_values) / len(f1_values), 4),
        "coverage": round(coverage, 4),
        "confusion_matrix": confusion,
        "per_class": per_class,
        "freshness_mae": freshness_mae,
        "freshness_mae_sample_count": (
            sum(
                truth is not None and guess is not None
                for truth, guess in zip(expected_freshness or [], predicted_freshness or [])
            )
            if expected_freshness is not None and predicted_freshness is not None
            else 0
        ),
    }
