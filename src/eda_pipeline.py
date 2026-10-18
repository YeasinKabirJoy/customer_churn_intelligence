"""Create reproducible Python EDA tables, charts, findings, and reconciliation evidence."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "telco_customer_churn_clean.csv"
SQL_KPI_PATH = PROJECT_ROOT / "data" / "processed" / "kpi_reference.csv"
SQL_SEGMENT_PATH = PROJECT_ROOT / "data" / "processed" / "segment_kpis.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"
PYTHON_KPI_PATH = OUTPUT_DIR / "python_kpi_reference.csv"
PYTHON_SEGMENT_PATH = OUTPUT_DIR / "python_segment_kpis.csv"
DISTRIBUTION_PATH = OUTPUT_DIR / "distribution_summary.csv"
FINDINGS_PATH = OUTPUT_DIR / "findings.csv"
RECONCILIATION_PATH = OUTPUT_DIR / "python_sql_reconciliation.csv"
SUMMARY_PATH = OUTPUT_DIR / "eda_validation_summary.json"
REPORT_PATH = PROJECT_ROOT / "docs" / "python_eda_report.md"

NAVY = "#17324D"
TEAL = "#138A8A"
ORANGE = "#E28A2B"
LIGHT_BLUE = "#7DB7D8"
GRAY = "#637381"
GRID = "#D9E2E8"
CHURN_COLORS = {"No": TEAL, "Yes": ORANGE}

SEGMENT_CONFIG = {
    "contract": {
        "column": "contract",
        "title": "How does churn vary by contract type?",
        "order": ["Month-to-month", "One year", "Two year"],
        "filename": "churn_by_contract.png",
    },
    "tenure_band": {
        "column": "tenure_band",
        "title": "How does churn vary across the customer lifecycle?",
        "order": ["0-12 months", "13-24 months", "25-48 months", "49-60 months", "61-72 months"],
        "filename": "churn_by_tenure_band.png",
    },
    "internet_service": {
        "column": "internet_service",
        "title": "How does churn vary by internet service?",
        "order": ["Fiber optic", "DSL", "No"],
        "filename": "churn_by_internet_service.png",
    },
    "payment_method": {
        "column": "payment_method",
        "title": "How does churn vary by payment method?",
        "order": [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ],
        "filename": "churn_by_payment_method.png",
    },
}


def configure_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": GRID,
            "axes.labelcolor": NAVY,
            "axes.titlecolor": NAVY,
            "axes.titleweight": "bold",
            "text.color": NAVY,
            "xtick.color": GRAY,
            "ytick.color": GRAY,
            "grid.color": GRID,
            "grid.alpha": 0.55,
            "font.family": "DejaVu Sans",
            "savefig.bbox": "tight",
            "savefig.dpi": 160,
        }
    )


def load_customers() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Run `python src/data_pipeline.py` before Python EDA.")
    return pd.read_csv(DATA_PATH)


def calculate_overall_kpis(customers: pd.DataFrame) -> pd.DataFrame:
    total = customers["customer_id"].nunique()
    churned = customers.loc[customers["churn_flag"] == 1, "customer_id"].nunique()
    retained = customers.loc[customers["churn_flag"] == 0, "customer_id"].nunique()
    return pd.DataFrame(
        [
            {
                "total_customers": total,
                "churned_customers": churned,
                "retained_customers": retained,
                "churn_rate": round(churned / total, 6),
                "total_monthly_charges": round(customers["monthly_charges"].sum(), 2),
                "average_monthly_charges": round(customers["monthly_charges"].mean(), 2),
                "missing_total_charges": int(customers["total_charges"].isna().sum()),
            }
        ]
    )


def wilson_interval(successes: pd.Series, totals: pd.Series, z: float = 1.96) -> tuple[pd.Series, pd.Series]:
    """Return a 95% Wilson interval for binomial rates."""
    proportion = successes / totals
    denominator = 1 + z**2 / totals
    center = (proportion + z**2 / (2 * totals)) / denominator
    margin = z * np.sqrt((proportion * (1 - proportion) + z**2 / (4 * totals)) / totals) / denominator
    return center - margin, center + margin


def calculate_segment_kpis(customers: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    dimensions = {
        "contract": "contract",
        "dependents": "dependents",
        "gender": "gender",
        "internet_service": "internet_service",
        "paperless_billing": "paperless_billing",
        "partner": "partner",
        "payment_method": "payment_method",
        "senior_citizen": "senior_citizen_label",
        "tenure_band": "tenure_band",
    }

    for dimension, column in dimensions.items():
        grouped = (
            customers.groupby(column, observed=True)
            .agg(
                total_customers=("customer_id", "nunique"),
                churned_customers=("churn_flag", "sum"),
            )
            .reset_index()
            .rename(columns={column: "segment"})
        )
        grouped.insert(0, "dimension", dimension)
        grouped["retained_customers"] = grouped["total_customers"] - grouped["churned_customers"]
        grouped["churn_rate"] = grouped["churned_customers"] / grouped["total_customers"]
        grouped["ci_low"], grouped["ci_high"] = wilson_interval(
            grouped["churned_customers"], grouped["total_customers"]
        )
        frames.append(grouped)

    result = pd.concat(frames, ignore_index=True)
    for column in ["churn_rate", "ci_low", "ci_high"]:
        result[column] = result[column].round(6)
    return result.sort_values(["dimension", "churn_rate"], ascending=[True, False]).reset_index(drop=True)


def calculate_distribution_summary(customers: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for churn, group in customers.groupby("churn", observed=True):
        for metric in ["tenure", "monthly_charges", "total_charges"]:
            values = group[metric]
            valid = values.dropna()
            rows.append(
                {
                    "churn": churn,
                    "metric": metric,
                    "customers": int(len(group)),
                    "non_missing": int(valid.size),
                    "missing": int(values.isna().sum()),
                    "mean": round(float(valid.mean()), 2),
                    "median": round(float(valid.median()), 2),
                    "p25": round(float(valid.quantile(0.25)), 2),
                    "p75": round(float(valid.quantile(0.75)), 2),
                    "minimum": round(float(valid.min()), 2),
                    "maximum": round(float(valid.max()), 2),
                }
            )
    return pd.DataFrame(rows)


def reconcile_with_sql(python_kpis: pd.DataFrame, python_segments: pd.DataFrame) -> pd.DataFrame:
    sql_kpis = pd.read_csv(SQL_KPI_PATH)
    sql_segments = pd.read_csv(SQL_SEGMENT_PATH)
    rows: list[dict[str, Any]] = []

    for metric in python_kpis.columns:
        python_value = float(python_kpis.loc[0, metric])
        sql_value = float(sql_kpis.loc[0, metric])
        tolerance = 1e-6 if metric == "churn_rate" else 1e-9
        rows.append(
            {
                "scope": "overall",
                "key": metric,
                "python_value": python_value,
                "sql_value": sql_value,
                "absolute_difference": abs(python_value - sql_value),
                "tolerance": tolerance,
                "status": "PASS" if math.isclose(python_value, sql_value, abs_tol=tolerance) else "FAIL",
            }
        )

    segment_columns = ["total_customers", "churned_customers", "retained_customers", "churn_rate"]
    merged = python_segments.merge(
        sql_segments[["dimension", "segment", *segment_columns]],
        on=["dimension", "segment"],
        suffixes=("_python", "_sql"),
        validate="one_to_one",
    )
    for record in merged.to_dict(orient="records"):
        for metric in segment_columns:
            python_value = float(record[f"{metric}_python"])
            sql_value = float(record[f"{metric}_sql"])
            tolerance = 1e-6 if metric == "churn_rate" else 0.0
            rows.append(
                {
                    "scope": "segment",
                    "key": f"{record['dimension']}::{record['segment']}::{metric}",
                    "python_value": python_value,
                    "sql_value": sql_value,
                    "absolute_difference": abs(python_value - sql_value),
                    "tolerance": tolerance,
                    "status": "PASS" if math.isclose(python_value, sql_value, abs_tol=tolerance) else "FAIL",
                }
            )
    return pd.DataFrame(rows)


def segment_record(segments: pd.DataFrame, dimension: str, segment: str) -> pd.Series:
    match = segments.loc[(segments["dimension"] == dimension) & (segments["segment"] == segment)]
    if len(match) != 1:
        raise ValueError(f"Expected one segment row for {dimension}={segment}")
    return match.iloc[0]


def build_findings(segments: pd.DataFrame, distributions: pd.DataFrame) -> pd.DataFrame:
    month = segment_record(segments, "contract", "Month-to-month")
    early = segment_record(segments, "tenure_band", "0-12 months")
    fiber = segment_record(segments, "internet_service", "Fiber optic")
    electronic = segment_record(segments, "payment_method", "Electronic check")
    monthly = distributions.loc[distributions["metric"] == "monthly_charges"].set_index("churn")
    total = distributions.loc[distributions["metric"] == "total_charges"].set_index("churn")

    return pd.DataFrame(
        [
            {
                "finding_id": "F-001",
                "evidence": f"Month-to-month customers: {int(month.total_customers):,} customers, {int(month.churned_customers):,} churned, {month.churn_rate:.1%} churn rate.",
                "interpretation": "Flexible-contract customers are strongly associated with observed churn concentration.",
                "limitation": "Contract choice is not randomized and overlaps with tenure, pricing, and customer preferences.",
                "next_action": "Compare contract groups within tenure bands and design a controlled offer test before claiming contract changes reduce churn.",
            },
            {
                "finding_id": "F-002",
                "evidence": f"Customers in months 0-12: {int(early.total_customers):,} customers, {int(early.churned_customers):,} churned, {early.churn_rate:.1%} churn rate.",
                "interpretation": "The early customer lifecycle is the clearest stage for deeper retention investigation.",
                "limitation": "Snapshot tenure is mechanically affected by survival; longer-tenure customers have already remained active longer.",
                "next_action": "Measure onboarding milestones, early support contacts, and service issues, then test a defined early-tenure intervention.",
            },
            {
                "finding_id": "F-003",
                "evidence": f"Fiber-optic customers: {int(fiber.total_customers):,} customers, {int(fiber.churned_customers):,} churned, {fiber.churn_rate:.1%} churn rate.",
                "interpretation": "The fiber customer experience, pricing, or customer mix warrants investigation.",
                "limitation": "The dataset lacks service quality, outage, support-contact, promotion, and local-market variables.",
                "next_action": "Join service-quality and support data before selecting an operational intervention.",
            },
            {
                "finding_id": "F-004",
                "evidence": f"Electronic-check customers: {int(electronic.total_customers):,} customers, {int(electronic.churned_customers):,} churned, {electronic.churn_rate:.1%} churn rate.",
                "interpretation": "Payment friction or characteristics correlated with electronic checks may be relevant.",
                "limitation": "Payment method may proxy for contract, tenure, digital behavior, or customer preference.",
                "next_action": "Compare payment methods within contract and tenure groups; test a payment-experience change with a control group.",
            },
            {
                "finding_id": "F-005",
                "evidence": f"Median monthly charges are {monthly.loc['Yes', 'median']:.2f} for churned versus {monthly.loc['No', 'median']:.2f} for retained customers; median total charges are {total.loc['Yes', 'median']:.2f} versus {total.loc['No', 'median']:.2f}.",
                "interpretation": "Churned customers tend to have higher current charges but lower accumulated charges, consistent with shorter tenure.",
                "limitation": "The distributions overlap, and total charges are strongly exposure-dependent because they accumulate with tenure.",
                "next_action": "Compare monthly charges within service and tenure groups; do not treat an unadjusted average difference as a price effect.",
            },
        ]
    )


def save_figure(figure: plt.Figure, filename: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURE_DIR / filename, facecolor="white")
    plt.close(figure)


def plot_overall_churn(kpis: pd.DataFrame) -> None:
    values = [int(kpis.loc[0, "retained_customers"]), int(kpis.loc[0, "churned_customers"])]
    labels = ["Retained", "Churned"]
    colors = [TEAL, ORANGE]
    figure, axis = plt.subplots(figsize=(8, 4.8))
    bars = axis.bar(labels, values, color=colors, width=0.58)
    total = sum(values)
    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            value + total * 0.018,
            f"{value:,}\n({value / total:.1%})",
            ha="center",
            va="bottom",
            fontweight="bold",
            color=NAVY,
        )
    axis.set_title("What is the overall customer churn outcome?", loc="left", pad=16)
    axis.set_ylabel("Distinct customers")
    axis.set_ylim(0, max(values) * 1.18)
    axis.grid(axis="x", visible=False)
    sns.despine(ax=axis)
    figure.text(0.01, 0.01, "Denominator: 7,043 distinct eligible customers", color=GRAY, fontsize=9)
    save_figure(figure, "overall_churn.png")


def plot_segment_rate_and_volume(segments: pd.DataFrame, dimension: str) -> None:
    config = SEGMENT_CONFIG[dimension]
    subset = segments.loc[segments["dimension"] == dimension].copy()
    subset["segment"] = pd.Categorical(subset["segment"], categories=config["order"], ordered=True)
    subset = subset.sort_values("segment", ascending=True)

    figure, (volume_axis, rate_axis) = plt.subplots(
        1,
        2,
        figsize=(12, max(4.2, len(subset) * 0.85)),
        gridspec_kw={"width_ratios": [1, 1.18]},
        sharey=True,
    )
    y = np.arange(len(subset))
    volume_axis.barh(y, subset["total_customers"], color=LIGHT_BLUE, height=0.58)
    rate_axis.barh(y, subset["churn_rate"], color=TEAL, height=0.58)

    for index, value in enumerate(subset["total_customers"]):
        volume_axis.text(value, index, f"  {int(value):,}", va="center", color=NAVY, fontsize=9)
    for index, row in enumerate(subset.itertuples()):
        rate_axis.text(row.churn_rate, index, f"  {row.churn_rate:.1%}  (n={int(row.churned_customers):,})", va="center", color=NAVY, fontsize=9)

    volume_axis.set_yticks(y, subset["segment"].astype(str))
    volume_axis.invert_yaxis()
    volume_axis.set_xlabel("Distinct customers")
    volume_axis.set_title("Segment volume", loc="left")
    rate_axis.set_xlabel("Churn rate")
    rate_axis.set_title("Churn rate and churned count", loc="left")
    rate_axis.xaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    rate_axis.set_xlim(0, max(0.55, subset["churn_rate"].max() * 1.34))
    volume_axis.set_xlim(0, subset["total_customers"].max() * 1.22)
    volume_axis.grid(axis="y", visible=False)
    rate_axis.grid(axis="y", visible=False)
    sns.despine(ax=volume_axis)
    sns.despine(ax=rate_axis)
    figure.suptitle(config["title"], x=0.01, ha="left", fontsize=15, fontweight="bold", color=NAVY)
    figure.text(0.01, 0.01, "Rate denominator: distinct customers within each displayed segment", color=GRAY, fontsize=9)
    figure.tight_layout(rect=(0, 0.04, 1, 0.93))
    save_figure(figure, config["filename"])


def plot_tenure_distribution(customers: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
    sns.histplot(
        data=customers,
        x="tenure",
        hue="churn",
        hue_order=["No", "Yes"],
        palette=CHURN_COLORS,
        stat="density",
        common_norm=False,
        element="step",
        fill=False,
        bins=24,
        linewidth=2,
        ax=axes[0],
    )
    sns.boxplot(
        data=customers,
        x="churn",
        y="tenure",
        order=["No", "Yes"],
        hue="churn",
        palette=CHURN_COLORS,
        legend=False,
        width=0.55,
        ax=axes[1],
    )
    axes[0].set_title("Full distribution", loc="left")
    axes[0].set_xlabel("Tenure (months)")
    axes[0].set_ylabel("Within-group density")
    axes[1].set_title("Median and spread", loc="left")
    axes[1].set_xlabel("Churn outcome")
    axes[1].set_ylabel("Tenure (months)")
    figure.suptitle("How does tenure distribution differ by churn outcome?", x=0.01, ha="left", fontsize=15, fontweight="bold", color=NAVY)
    figure.tight_layout(rect=(0, 0, 1, 0.93))
    save_figure(figure, "tenure_distribution_by_churn.png")


def plot_charge_distributions(customers: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    sns.boxplot(
        data=customers,
        x="churn",
        y="monthly_charges",
        order=["No", "Yes"],
        hue="churn",
        palette=CHURN_COLORS,
        legend=False,
        width=0.55,
        ax=axes[0],
    )
    sns.boxplot(
        data=customers,
        x="churn",
        y="total_charges",
        order=["No", "Yes"],
        hue="churn",
        palette=CHURN_COLORS,
        legend=False,
        width=0.55,
        ax=axes[1],
    )
    axes[0].set_title("Monthly charges", loc="left")
    axes[0].set_xlabel("Churn outcome")
    axes[0].set_ylabel("Monthly charges")
    axes[1].set_title("Total charges", loc="left")
    axes[1].set_xlabel("Churn outcome")
    axes[1].set_ylabel("Total charges")
    figure.suptitle("How do charge distributions differ by churn outcome?", x=0.01, ha="left", fontsize=15, fontweight="bold", color=NAVY)
    figure.text(0.01, 0.01, "Total-charge chart excludes 11 missing values and retains all other customers.", color=GRAY, fontsize=9)
    figure.tight_layout(rect=(0, 0.04, 1, 0.93))
    save_figure(figure, "charge_distributions_by_churn.png")


def render_report(
    kpis: pd.DataFrame,
    distributions: pd.DataFrame,
    findings: pd.DataFrame,
    reconciliation: pd.DataFrame,
) -> str:
    distribution_lookup = distributions.set_index(["metric", "churn"])
    finding_sections = "\n\n".join(
        f"""### {row.finding_id}

- **Evidence:** {row.evidence}
- **Interpretation:** {row.interpretation}
- **Limitation:** {row.limitation}
- **Next action:** {row.next_action}"""
        for row in findings.itertuples()
    )
    return f"""# Python EDA report

Generated by `python src/eda_pipeline.py` from the Phase 2 processed table.

## Reconciled overall KPIs

- Total customers: {int(kpis.loc[0, 'total_customers']):,}
- Churned customers: {int(kpis.loc[0, 'churned_customers']):,}
- Retained customers: {int(kpis.loc[0, 'retained_customers']):,}
- Churn rate: {kpis.loc[0, 'churn_rate']:.3%}
- Average monthly charges: {kpis.loc[0, 'average_monthly_charges']:.2f}

All {len(reconciliation):,} overall and segment comparisons with SQL passed within their documented tolerances.

## Distribution context

| Metric | Retained median | Churned median | Retained middle 50% | Churned middle 50% |
|---|---:|---:|---:|---:|
| Tenure (months) | {distribution_lookup.loc[('tenure', 'No'), 'median']:.2f} | {distribution_lookup.loc[('tenure', 'Yes'), 'median']:.2f} | {distribution_lookup.loc[('tenure', 'No'), 'p25']:.2f}-{distribution_lookup.loc[('tenure', 'No'), 'p75']:.2f} | {distribution_lookup.loc[('tenure', 'Yes'), 'p25']:.2f}-{distribution_lookup.loc[('tenure', 'Yes'), 'p75']:.2f} |
| Monthly charges | {distribution_lookup.loc[('monthly_charges', 'No'), 'median']:.2f} | {distribution_lookup.loc[('monthly_charges', 'Yes'), 'median']:.2f} | {distribution_lookup.loc[('monthly_charges', 'No'), 'p25']:.2f}-{distribution_lookup.loc[('monthly_charges', 'No'), 'p75']:.2f} | {distribution_lookup.loc[('monthly_charges', 'Yes'), 'p25']:.2f}-{distribution_lookup.loc[('monthly_charges', 'Yes'), 'p75']:.2f} |
| Total charges | {distribution_lookup.loc[('total_charges', 'No'), 'median']:.2f} | {distribution_lookup.loc[('total_charges', 'Yes'), 'median']:.2f} | {distribution_lookup.loc[('total_charges', 'No'), 'p25']:.2f}-{distribution_lookup.loc[('total_charges', 'No'), 'p75']:.2f} | {distribution_lookup.loc[('total_charges', 'Yes'), 'p25']:.2f}-{distribution_lookup.loc[('total_charges', 'Yes'), 'p75']:.2f} |

Medians and interquartile ranges are included because averages alone can hide skew and overlapping distributions.

## Findings

{finding_sections}

## Chart design rules applied

- Each chart starts with a business question.
- Axes and units are labeled.
- Every churn-rate chart displays segment volume and churned-customer count.
- Distribution charts show spread rather than only group averages.
- Color meaning is consistent: teal for retained and orange for churned where outcome color is used.
- Claims use association language and include limitations.
"""


def run_eda() -> dict[str, Any]:
    configure_style()
    customers = load_customers()
    kpis = calculate_overall_kpis(customers)
    segments = calculate_segment_kpis(customers)
    distributions = calculate_distribution_summary(customers)
    reconciliation = reconcile_with_sql(kpis, segments)
    failed = reconciliation.loc[reconciliation["status"] != "PASS"]
    if not failed.empty:
        raise ValueError(f"Python/SQL reconciliation failed for: {failed['key'].tolist()}")
    findings = build_findings(segments, distributions)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    kpis.to_csv(PYTHON_KPI_PATH, index=False, lineterminator="\n")
    segments.to_csv(PYTHON_SEGMENT_PATH, index=False, lineterminator="\n")
    distributions.to_csv(DISTRIBUTION_PATH, index=False, lineterminator="\n")
    findings.to_csv(FINDINGS_PATH, index=False, lineterminator="\n")
    reconciliation.to_csv(RECONCILIATION_PATH, index=False, lineterminator="\n")

    plot_overall_churn(kpis)
    for dimension in SEGMENT_CONFIG:
        plot_segment_rate_and_volume(segments, dimension)
    plot_tenure_distribution(customers)
    plot_charge_distributions(customers)

    REPORT_PATH.write_text(
        render_report(kpis, distributions, findings, reconciliation), encoding="utf-8"
    )
    summary = {
        "status": "PASS",
        "customers": int(kpis.loc[0, "total_customers"]),
        "figures_created": 7,
        "findings_documented": int(len(findings)),
        "reconciliation_checks": int(len(reconciliation)),
        "failed_reconciliation_checks": int(len(failed)),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run_eda(), indent=2))
