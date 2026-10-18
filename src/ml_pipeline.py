"""Train and evaluate lightweight churn risk-ranking models.

This is a portfolio proof of concept, not a deployment pipeline. The final test set
is used once for reporting; preprocessing is fitted inside each training pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    PrecisionRecallDisplay,
)
from sklearn.calibration import calibration_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "telco_customer_churn_clean.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "ml"
EXPORT_DIR = PROJECT_ROOT / "data" / "processed"
RANDOM_STATE = 42
TEST_SIZE = 0.20
CONTACT_CAPACITY = 0.20

NUMERIC_FEATURES = ["senior_citizen", "tenure", "monthly_charges"]
CATEGORICAL_FEATURES = [
    "gender", "partner", "dependents", "phone_service", "multiple_lines",
    "internet_service", "online_security", "online_backup", "device_protection",
    "tech_support", "streaming_tv", "streaming_movies", "contract",
    "paperless_billing", "payment_method",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "churn_flag"


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", drop="if_binary")),
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ])


def build_models() -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline([
            ("preprocess", build_preprocessor()),
            ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
        ]),
        "shallow_decision_tree": Pipeline([
            ("preprocess", build_preprocessor()),
            ("model", DecisionTreeClassifier(max_depth=4, min_samples_leaf=100, random_state=RANDOM_STATE)),
        ]),
    }


def model_metrics(name: str, y_true: pd.Series, probability: np.ndarray) -> dict[str, float | int | str]:
    prediction = (probability >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction).ravel()
    capacity_count = int(np.ceil(len(probability) * CONTACT_CAPACITY))
    top_indices = np.argsort(-probability)[:capacity_count]
    captured = int(y_true.iloc[top_indices].sum())
    total_churners = int(y_true.sum())
    return {
        "model": name,
        "test_customers": int(len(y_true)),
        "test_churners": total_churners,
        "roc_auc": roc_auc_score(y_true, probability),
        "average_precision": average_precision_score(y_true, probability),
        "precision_at_0_5": precision_score(y_true, prediction, zero_division=0),
        "recall_at_0_5": recall_score(y_true, prediction, zero_division=0),
        "f1_at_0_5": f1_score(y_true, prediction, zero_division=0),
        "brier_score": brier_score_loss(y_true, probability),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "top_20_percent_customers": capacity_count,
        "churners_captured_top_20_percent": captured,
        "recall_at_top_20_percent": captured / total_churners,
        "lift_at_top_20_percent": (captured / capacity_count) / y_true.mean(),
    }


def fairness_slices(test: pd.DataFrame, probability: np.ndarray) -> pd.DataFrame:
    frame = test[[TARGET, "gender", "senior_citizen_label"]].copy()
    frame["probability"] = probability
    frame["prediction"] = (probability >= 0.5).astype(int)
    cutoff = np.sort(probability)[-int(np.ceil(len(probability) * CONTACT_CAPACITY))]
    frame["selected_top_20_percent"] = probability >= cutoff
    rows = []
    for attribute in ["gender", "senior_citizen_label"]:
        for group, part in frame.groupby(attribute, dropna=False):
            positives = int(part[TARGET].sum())
            true_positives = int(((part[TARGET] == 1) & (part["prediction"] == 1)).sum())
            rows.append({
                "attribute": attribute,
                "group": str(group),
                "customers": len(part),
                "actual_churn_rate": part[TARGET].mean(),
                "average_predicted_risk": part["probability"].mean(),
                "recall_at_0_5": true_positives / positives if positives else np.nan,
                "selection_rate_top_20_percent": part["selected_top_20_percent"].mean(),
            })
    return pd.DataFrame(rows)


def feature_associations(model: Pipeline) -> pd.DataFrame:
    names = model.named_steps["preprocess"].get_feature_names_out()
    coefficients = model.named_steps["model"].coef_[0]
    result = pd.DataFrame({"feature": names, "coefficient": coefficients})
    result["odds_ratio"] = np.exp(result["coefficient"])
    result["absolute_coefficient"] = result["coefficient"].abs()
    result["direction"] = np.where(result["coefficient"] >= 0, "higher modeled risk", "lower modeled risk")
    return result.sort_values("absolute_coefficient", ascending=False).reset_index(drop=True)


def risk_deciles(y_true: pd.Series, probability: np.ndarray) -> pd.DataFrame:
    frame = pd.DataFrame({"actual_churn": y_true.to_numpy(), "predicted_probability": probability})
    frame["risk_decile"] = pd.qcut(frame["predicted_probability"], 10, labels=False, duplicates="drop") + 1
    result = frame.groupby("risk_decile", as_index=False).agg(
        customers=("actual_churn", "size"),
        churned_customers=("actual_churn", "sum"),
        actual_churn_rate=("actual_churn", "mean"),
        average_predicted_risk=("predicted_probability", "mean"),
    )
    result["risk_decile"] = 11 - result["risk_decile"]
    return result.sort_values("risk_decile").reset_index(drop=True)


def render_figures(y_true: pd.Series, probabilities: dict[str, np.ndarray], deciles: pd.DataFrame, tree: Pipeline) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for name, probability in probabilities.items():
        label = name.replace("_", " ").title()
        RocCurveDisplay.from_predictions(y_true, probability, name=label, ax=axes[0])
        PrecisionRecallDisplay.from_predictions(y_true, probability, name=label, ax=axes[1])
    axes[0].set_title("ROC curve — held-out test set")
    axes[1].set_title("Precision-recall curve — held-out test set")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "model_comparison_curves.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    for axis, (name, probability) in zip(axes[:2], probabilities.items()):
        ConfusionMatrixDisplay.from_predictions(
            y_true,
            (probability >= 0.5).astype(int),
            display_labels=["Retained", "Churned"],
            colorbar=False,
            cmap="Blues",
            ax=axis,
        )
        axis.set_title(name.replace("_", " ").title())
    for name, probability in probabilities.items():
        observed, predicted = calibration_curve(y_true, probability, n_bins=8, strategy="quantile")
        axes[2].plot(predicted, observed, marker="o", label=name.replace("_", " ").title())
    axes[2].plot([0, 1], [0, 1], linestyle="--", color="#637381", label="Ideal")
    axes[2].set(title="Probability calibration", xlabel="Average predicted probability", ylabel="Observed churn rate")
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "confusion_and_calibration.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(deciles["risk_decile"].astype(str), deciles["actual_churn_rate"], color="#138A8A")
    ax.plot(deciles["risk_decile"].astype(str), deciles["average_predicted_risk"], color="#E28A2B", marker="o", label="Average predicted risk")
    ax.set(title="Observed churn by predicted-risk decile", xlabel="Risk decile (1 = highest risk)", ylabel="Rate")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "risk_decile_performance.png", dpi=160)
    plt.close(fig)

    feature_names = tree.named_steps["preprocess"].get_feature_names_out()
    fig, ax = plt.subplots(figsize=(18, 9))
    plot_tree(tree.named_steps["model"], feature_names=feature_names, class_names=["Retained", "Churned"], filled=True, rounded=True, fontsize=7, ax=ax)
    ax.set_title("Shallow comparison tree — training data only")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "shallow_decision_tree.png", dpi=160)
    plt.close(fig)


def run_ml_pipeline() -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    customers = pd.read_csv(DATA_PATH)
    train, test = train_test_split(customers, test_size=TEST_SIZE, stratify=customers[TARGET], random_state=RANDOM_STATE)
    models = build_models()
    probabilities: dict[str, np.ndarray] = {}
    metrics = []
    for name, pipeline in models.items():
        pipeline.fit(train[FEATURES], train[TARGET])
        probability = pipeline.predict_proba(test[FEATURES])[:, 1]
        probabilities[name] = probability
        metrics.append(model_metrics(name, test[TARGET].reset_index(drop=True), probability))
        joblib.dump(pipeline, OUTPUT_DIR / f"{name}.joblib")

    primary_probability = probabilities["logistic_regression"]
    y_test = test[TARGET].reset_index(drop=True)
    metric_frame = pd.DataFrame(metrics)
    metric_frame.to_csv(OUTPUT_DIR / "model_metrics.csv", index=False)
    feature_associations(models["logistic_regression"]).to_csv(OUTPUT_DIR / "logistic_feature_associations.csv", index=False)
    fairness_slices(test.reset_index(drop=True), primary_probability).to_csv(OUTPUT_DIR / "fairness_slices.csv", index=False)
    deciles = risk_deciles(y_test, primary_probability)
    deciles.to_csv(OUTPUT_DIR / "risk_deciles.csv", index=False)

    predictions = test[["customer_id", "gender", "senior_citizen_label"]].reset_index(drop=True)
    predictions["actual_churn"] = y_test
    predictions["predicted_churn_probability"] = primary_probability
    predictions["predicted_at_0_5"] = (primary_probability >= 0.5).astype(int)
    predictions["evaluation_split"] = "test"
    predictions.to_csv(EXPORT_DIR / "ml_test_predictions.csv", index=False)

    render_figures(y_test, probabilities, deciles, models["shallow_decision_tree"])
    summary = {
        "scope": "proof-of-concept risk ranking; not production deployment",
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "train_customers": len(train),
        "test_customers": len(test),
        "features": FEATURES,
        "excluded_fields": ["customer_id", "churn", "churn_flag", "total_charges", "total_charges_missing", "tenure_band", "senior_citizen_label"],
        "primary_model": "logistic_regression",
        "metrics": metrics,
    }
    (OUTPUT_DIR / "model_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run_ml_pipeline(), indent=2))

