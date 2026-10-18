"""Tests for Python EDA calculations and SQL reconciliation."""

from __future__ import annotations

import pandas as pd
import pytest

from src.eda_pipeline import (
    DATA_PATH,
    FIGURE_DIR,
    SEGMENT_CONFIG,
    calculate_distribution_summary,
    calculate_overall_kpis,
    calculate_segment_kpis,
    reconcile_with_sql,
    run_eda,
)


@pytest.fixture(scope="module")
def customers() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def test_python_overall_kpis_are_internally_consistent(customers: pd.DataFrame) -> None:
    kpis = calculate_overall_kpis(customers).iloc[0]
    assert kpis["churned_customers"] + kpis["retained_customers"] == kpis["total_customers"]
    assert kpis["churn_rate"] == pytest.approx(
        kpis["churned_customers"] / kpis["total_customers"], abs=1e-6
    )


def test_each_python_segment_dimension_reconciles(customers: pd.DataFrame) -> None:
    segments = calculate_segment_kpis(customers)
    total = customers["customer_id"].nunique()
    churned = customers.loc[customers["churn_flag"] == 1, "customer_id"].nunique()
    grouped = segments.groupby("dimension").agg(
        total_customers=("total_customers", "sum"),
        churned_customers=("churned_customers", "sum"),
    )
    assert grouped["total_customers"].eq(total).all()
    assert grouped["churned_customers"].eq(churned).all()


def test_wilson_intervals_are_valid(customers: pd.DataFrame) -> None:
    segments = calculate_segment_kpis(customers)
    assert segments["ci_low"].between(0, 1).all()
    assert segments["ci_high"].between(0, 1).all()
    assert (segments["ci_low"] <= segments["churn_rate"]).all()
    assert (segments["churn_rate"] <= segments["ci_high"]).all()


def test_distribution_counts_preserve_group_denominators(customers: pd.DataFrame) -> None:
    distributions = calculate_distribution_summary(customers)
    for row in distributions.itertuples():
        assert row.non_missing + row.missing == row.customers


def test_python_and_sql_reconcile(customers: pd.DataFrame) -> None:
    reconciliation = reconcile_with_sql(
        calculate_overall_kpis(customers), calculate_segment_kpis(customers)
    )
    assert reconciliation["status"].eq("PASS").all()


def test_eda_pipeline_creates_all_figures() -> None:
    summary = run_eda()
    expected = {
        "overall_churn.png",
        "tenure_distribution_by_churn.png",
        "charge_distributions_by_churn.png",
        *(config["filename"] for config in SEGMENT_CONFIG.values()),
    }
    assert summary["figures_created"] == len(expected)
    assert all((FIGURE_DIR / filename).stat().st_size > 0 for filename in expected)
