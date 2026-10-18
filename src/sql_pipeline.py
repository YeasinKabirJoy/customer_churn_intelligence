"""Build the governed SQLite layer and export reconciled reference tables."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "telco_customer_churn_clean.csv"
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "telco_churn.sqlite"
SQL_DIR = PROJECT_ROOT / "sql"
KPI_EXPORT = PROJECT_ROOT / "data" / "processed" / "kpi_reference.csv"
SEGMENT_EXPORT = PROJECT_ROOT / "data" / "processed" / "segment_kpis.csv"
CHARGE_EXPORT = PROJECT_ROOT / "data" / "processed" / "charge_summary_by_churn.csv"
CHECK_EXPORT = PROJECT_ROOT / "data" / "processed" / "sql_sanity_checks.csv"
SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "sql_validation_summary.json"


def read_sql(filename: str) -> str:
    return (SQL_DIR / filename).read_text(encoding="utf-8")


def normalize_for_sql(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert CSV values into SQLite-compatible Python values."""
    normalized = frame.copy()
    normalized["senior_citizen"] = normalized["senior_citizen"].astype(int)
    normalized["tenure"] = normalized["tenure"].astype(int)
    normalized["churn_flag"] = normalized["churn_flag"].astype(int)
    normalized["total_charges_missing"] = normalized["total_charges_missing"].map(
        {True: 1, False: 0, "True": 1, "False": 0}
    ).astype(int)
    return normalized.astype(object).where(pd.notna(normalized), None)


def insert_customers(connection: sqlite3.Connection, frame: pd.DataFrame) -> None:
    columns = frame.columns.tolist()
    placeholders = ", ".join("?" for _ in columns)
    quoted_columns = ", ".join(f'"{column}"' for column in columns)
    sql = f"INSERT INTO customer_churn ({quoted_columns}) VALUES ({placeholders})"
    connection.executemany(sql, frame.itertuples(index=False, name=None))


def query_frame(connection: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, connection)


def build_database(database_path: Path = DATABASE_PATH) -> dict[str, Any]:
    """Recreate the SQLite database, validate it, and export governed results."""
    if not PROCESSED_CSV.exists():
        raise FileNotFoundError("Run `python src/data_pipeline.py` before building SQLite.")

    customers = normalize_for_sql(pd.read_csv(PROCESSED_CSV))
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.executescript(read_sql("01_schema.sql"))
        insert_customers(connection, customers)
        connection.executescript(read_sql("02_views.sql"))
        connection.commit()

        kpis = query_frame(connection, read_sql("03_kpis.sql"))
        segments = query_frame(connection, read_sql("04_segments.sql"))
        charges = query_frame(connection, read_sql("05_charge_summary.sql"))
        checks = query_frame(connection, read_sql("06_sanity_checks.sql"))

    failed_checks = checks.loc[checks["status"] != "PASS", "check_name"].tolist()
    if failed_checks:
        raise ValueError(f"SQL reconciliation checks failed: {failed_checks}")

    # Exports are presentation-neutral sources for Python and both BI tools.
    kpis.to_csv(KPI_EXPORT, index=False, lineterminator="\n")
    segments.to_csv(SEGMENT_EXPORT, index=False, lineterminator="\n")
    charges.to_csv(CHARGE_EXPORT, index=False, lineterminator="\n")
    checks.to_csv(CHECK_EXPORT, index=False, lineterminator="\n")

    summary = {
        "status": "PASS",
        "database": database_path.name,
        "loaded_rows": int(len(customers)),
        "overall_kpis": kpis.iloc[0].to_dict(),
        "segment_rows": int(len(segments)),
        "sanity_checks": int(len(checks)),
        "failed_checks": failed_checks,
        "exports": [
            KPI_EXPORT.name,
            SEGMENT_EXPORT.name,
            CHARGE_EXPORT.name,
            CHECK_EXPORT.name,
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build_database(), indent=2))
