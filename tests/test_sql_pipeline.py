"""Cross-check the SQLite analytical layer against the processed data."""

from __future__ import annotations

import sqlite3

import pandas as pd
import pytest

from src.sql_pipeline import DATABASE_PATH, PROCESSED_CSV, build_database


@pytest.fixture(scope="module", autouse=True)
def built_database() -> None:
    build_database()


def test_loaded_rows_equal_processed_rows() -> None:
    processed = pd.read_csv(PROCESSED_CSV)
    with sqlite3.connect(DATABASE_PATH) as connection:
        loaded = connection.execute("SELECT COUNT(*) FROM customer_churn").fetchone()[0]
    assert loaded == len(processed)


def test_sql_kpis_match_independent_pandas_calculation() -> None:
    processed = pd.read_csv(PROCESSED_CSV)
    with sqlite3.connect(DATABASE_PATH) as connection:
        sql = pd.read_sql_query("SELECT * FROM vw_overall_kpis", connection).iloc[0]

    expected_total = processed["customer_id"].nunique()
    expected_churned = processed.loc[processed["churn_flag"] == 1, "customer_id"].nunique()
    expected_retained = processed.loc[processed["churn_flag"] == 0, "customer_id"].nunique()

    assert sql["total_customers"] == expected_total
    assert sql["churned_customers"] == expected_churned
    assert sql["retained_customers"] == expected_retained
    assert sql["churn_rate"] == pytest.approx(expected_churned / expected_total, abs=1e-12)
    assert sql["total_monthly_charges"] == pytest.approx(processed["monthly_charges"].sum())
    assert sql["average_monthly_charges"] == pytest.approx(processed["monthly_charges"].mean())


def test_each_segment_dimension_reconciles_to_overall() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        overall = connection.execute(
            "SELECT total_customers, churned_customers FROM vw_overall_kpis"
        ).fetchone()
        reconciled = pd.read_sql_query(
            """
            SELECT dimension,
                   SUM(total_customers) AS total_customers,
                   SUM(churned_customers) AS churned_customers
            FROM vw_segment_kpis
            GROUP BY dimension
            """,
            connection,
        )

    assert reconciled["total_customers"].eq(overall[0]).all()
    assert reconciled["churned_customers"].eq(overall[1]).all()


def test_churned_plus_retained_equals_total() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        total, churned, retained = connection.execute(
            "SELECT total_customers, churned_customers, retained_customers FROM vw_overall_kpis"
        ).fetchone()
    assert churned + retained == total


def test_all_sql_sanity_checks_pass() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        checks = pd.read_sql_query(
            (DATABASE_PATH.parents[2] / "sql" / "06_sanity_checks.sql").read_text(encoding="utf-8"),
            connection,
        )
    assert checks["status"].eq("PASS").all()
