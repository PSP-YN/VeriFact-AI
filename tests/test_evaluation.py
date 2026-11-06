import pytest

from app.evaluation import evaluate_verdicts


def test_evaluation_accuracy_macro_f1_coverage_and_confusion():
    report = evaluate_verdicts(
        ["supported", "contradicted", "inconclusive"],
        ["supported", "supported", "inconclusive"],
    )
    assert report["accuracy"] == pytest.approx(2 / 3, abs=0.0001)
    assert report["coverage"] == pytest.approx(2 / 3, abs=0.0001)
    assert report["confusion_matrix"]["contradicted"]["supported"] == 1


def test_freshness_mae_uses_only_known_pairs():
    report = evaluate_verdicts(
        ["supported", "potentially_stale"],
        ["supported", "potentially_stale"],
        expected_freshness=[90, 20],
        predicted_freshness=[80, None],
    )
    assert report["freshness_mae"] == 10
    assert report["freshness_mae_sample_count"] == 1


def test_evaluation_rejects_length_mismatch():
    with pytest.raises(ValueError):
        evaluate_verdicts(["supported"], ["supported", "inconclusive"])
