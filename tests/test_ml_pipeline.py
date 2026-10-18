"""Tests for the Phase 7 proof-of-concept ML pipeline."""

import json

import pandas as pd

from src.ml_pipeline import DATA_PATH, FEATURES, OUTPUT_DIR, TARGET, run_ml_pipeline


def test_feature_contract_prevents_direct_target_leakage() -> None:
    forbidden = {"customer_id", "churn", "churn_flag", "total_charges", "tenure_band"}
    assert forbidden.isdisjoint(FEATURES)
    assert TARGET not in FEATURES


def test_ml_pipeline_is_reproducible_and_writes_outputs() -> None:
    first = run_ml_pipeline()
    first_metrics = pd.read_csv(OUTPUT_DIR / "model_metrics.csv")
    second = run_ml_pipeline()
    second_metrics = pd.read_csv(OUTPUT_DIR / "model_metrics.csv")
    pd.testing.assert_frame_equal(first_metrics, second_metrics)
    assert first["train_customers"] + first["test_customers"] == len(pd.read_csv(DATA_PATH))
    assert second["primary_model"] == "logistic_regression"


def test_metrics_and_capacity_results_are_valid() -> None:
    metrics = pd.read_csv(OUTPUT_DIR / "model_metrics.csv")
    for column in ["roc_auc", "average_precision", "precision_at_0_5", "recall_at_0_5", "f1_at_0_5", "recall_at_top_20_percent"]:
        assert metrics[column].between(0, 1).all()
    assert (metrics["lift_at_top_20_percent"] > 0).all()


def test_prediction_and_fairness_exports_are_complete() -> None:
    summary = json.loads((OUTPUT_DIR / "model_summary.json").read_text(encoding="utf-8"))
    predictions = pd.read_csv(OUTPUT_DIR.parents[1] / "data" / "processed" / "ml_test_predictions.csv")
    fairness = pd.read_csv(OUTPUT_DIR / "fairness_slices.csv")
    assert len(predictions) == summary["test_customers"]
    assert predictions["predicted_churn_probability"].between(0, 1).all()
    assert set(fairness["attribute"]) == {"gender", "senior_citizen_label"}


def test_ml_visuals_exist() -> None:
    run_ml_pipeline()
    for name in ["model_comparison_curves.png", "confusion_and_calibration.png", "risk_decile_performance.png", "shallow_decision_tree.png"]:
        assert (OUTPUT_DIR / name).stat().st_size > 0

