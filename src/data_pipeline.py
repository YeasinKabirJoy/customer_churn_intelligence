"""Audit, clean, validate, and export the Telco Customer Churn dataset."""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "telco_customer_churn_clean.csv"
VALIDATION_PATH = PROJECT_ROOT / "data" / "processed" / "validation_summary.json"
QUALITY_REPORT_PATH = PROJECT_ROOT / "docs" / "data_quality_report.md"

EXPECTED_COLUMNS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
]

COLUMN_RENAMES = {
    "customerID": "customer_id",
    "SeniorCitizen": "senior_citizen",
    "Partner": "partner",
    "Dependents": "dependents",
    "PhoneService": "phone_service",
    "MultipleLines": "multiple_lines",
    "InternetService": "internet_service",
    "OnlineSecurity": "online_security",
    "OnlineBackup": "online_backup",
    "DeviceProtection": "device_protection",
    "TechSupport": "tech_support",
    "StreamingTV": "streaming_tv",
    "StreamingMovies": "streaming_movies",
    "Contract": "contract",
    "PaperlessBilling": "paperless_billing",
    "PaymentMethod": "payment_method",
    "MonthlyCharges": "monthly_charges",
    "TotalCharges": "total_charges",
    "Churn": "churn",
}

ALLOWED_CATEGORIES = {
    "gender": {"Female", "Male"},
    "senior_citizen": {0, 1},
    "partner": {"No", "Yes"},
    "dependents": {"No", "Yes"},
    "phone_service": {"No", "Yes"},
    "multiple_lines": {"No", "No phone service", "Yes"},
    "internet_service": {"DSL", "Fiber optic", "No"},
    "online_security": {"No", "No internet service", "Yes"},
    "online_backup": {"No", "No internet service", "Yes"},
    "device_protection": {"No", "No internet service", "Yes"},
    "tech_support": {"No", "No internet service", "Yes"},
    "streaming_tv": {"No", "No internet service", "Yes"},
    "streaming_movies": {"No", "No internet service", "Yes"},
    "contract": {"Month-to-month", "One year", "Two year"},
    "paperless_billing": {"No", "Yes"},
    "payment_method": {
        "Bank transfer (automatic)",
        "Credit card (automatic)",
        "Electronic check",
        "Mailed check",
    },
    "churn": {"No", "Yes"},
}

TENURE_LABELS = ["0-12 months", "13-24 months", "25-48 months", "49-60 months", "61-72 months"]


def file_sha256(path: Path) -> str:
    """Return an uppercase SHA-256 hash for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load every source field as text so the audit sees the original representation."""
    return pd.read_csv(path, dtype="string", keep_default_na=False, encoding="utf-8")


def audit_raw(raw: pd.DataFrame) -> dict[str, Any]:
    """Profile source structure without changing it."""
    stripped = raw.apply(lambda column: column.str.strip())
    blank_counts = stripped.eq("").sum()
    numeric_audit: dict[str, dict[str, Any]] = {}

    for column in ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]:
        converted = pd.to_numeric(stripped[column].replace("", pd.NA), errors="coerce")
        numeric_audit[column] = {
            "conversion_failures_or_blanks": int(converted.isna().sum()),
            "minimum": None if converted.dropna().empty else float(converted.min()),
            "maximum": None if converted.dropna().empty else float(converted.max()),
        }

    return {
        "rows": int(len(raw)),
        "columns": int(raw.shape[1]),
        "column_names": raw.columns.tolist(),
        "duplicate_rows": int(raw.duplicated().sum()),
        "duplicate_customer_ids": int(stripped["customerID"].duplicated().sum()),
        "blank_customer_ids": int(stripped["customerID"].eq("").sum()),
        "blank_cells_by_column": {name: int(count) for name, count in blank_counts.items()},
        "numeric_audit": numeric_audit,
    }


def clean_customer_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Apply explicit, row-preserving cleaning and analytical derivations."""
    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(raw.columns))
    unexpected_columns = sorted(set(raw.columns) - set(EXPECTED_COLUMNS))
    if missing_columns or unexpected_columns:
        raise ValueError(
            f"Schema mismatch. Missing={missing_columns}; unexpected={unexpected_columns}"
        )

    clean = raw.loc[:, EXPECTED_COLUMNS].copy()
    for column in clean.columns:
        clean[column] = clean[column].str.strip().replace("", pd.NA)

    clean = clean.rename(columns=COLUMN_RENAMES)
    clean["senior_citizen"] = pd.to_numeric(clean["senior_citizen"], errors="raise").astype("Int64")
    clean["tenure"] = pd.to_numeric(clean["tenure"], errors="raise").astype("Int64")
    clean["monthly_charges"] = pd.to_numeric(clean["monthly_charges"], errors="raise").astype("Float64")
    clean["total_charges"] = pd.to_numeric(clean["total_charges"], errors="coerce").astype("Float64")

    clean["senior_citizen_label"] = clean["senior_citizen"].map({0: "No", 1: "Yes"}).astype("string")
    clean["churn_flag"] = clean["churn"].map({"No": 0, "Yes": 1}).astype("Int64")
    clean["total_charges_missing"] = clean["total_charges"].isna()
    clean["tenure_band"] = pd.cut(
        clean["tenure"],
        bins=[-1, 12, 24, 48, 60, 72],
        labels=TENURE_LABELS,
        ordered=True,
    )
    return clean


def validate(raw: pd.DataFrame, clean: pd.DataFrame, audit: dict[str, Any]) -> dict[str, Any]:
    """Return named checks and fail the pipeline if a critical check fails."""
    category_checks = {
        column: set(clean[column].dropna().unique()).issubset(allowed)
        for column, allowed in ALLOWED_CATEGORIES.items()
    }
    checks = {
        "expected_source_schema": raw.columns.tolist() == EXPECTED_COLUMNS,
        "row_count_preserved": len(clean) == len(raw),
        "no_duplicate_source_rows": audit["duplicate_rows"] == 0,
        "customer_id_complete": clean["customer_id"].notna().all(),
        "customer_id_unique": clean["customer_id"].is_unique,
        "tenure_in_range_0_72": clean["tenure"].between(0, 72).all(),
        "monthly_charges_nonnegative": clean["monthly_charges"].ge(0).all(),
        "total_charges_nonnegative_when_present": clean["total_charges"].dropna().ge(0).all(),
        "total_charges_missingness_preserved": (
            clean["total_charges"].isna().sum()
            == audit["blank_cells_by_column"]["TotalCharges"]
        ),
        "missing_total_charges_have_zero_tenure": clean.loc[
            clean["total_charges"].isna(), "tenure"
        ].eq(0).all(),
        "churn_flag_complete": clean["churn_flag"].notna().all(),
        "tenure_band_complete": clean["tenure_band"].notna().all(),
        "allowed_categories": all(category_checks.values()),
    }
    failed = [name for name, passed in checks.items() if not bool(passed)]

    summary = {
        "status": "PASS" if not failed else "FAIL",
        "source_file": RAW_PATH.name,
        "source_sha256": file_sha256(RAW_PATH),
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "source_rows": int(len(raw)),
        "processed_rows": int(len(clean)),
        "source_columns": int(raw.shape[1]),
        "processed_columns": int(clean.shape[1]),
        "records_dropped": int(len(raw) - len(clean)),
        "total_charges_missing": int(clean["total_charges"].isna().sum()),
        "checks": {name: bool(value) for name, value in checks.items()},
        "category_checks": {name: bool(value) for name, value in category_checks.items()},
        "failed_checks": failed,
    }
    if failed:
        raise ValueError(f"Critical validation checks failed: {failed}")
    return summary


def render_quality_report(audit: dict[str, Any], summary: dict[str, Any]) -> str:
    """Create a human-readable, evidence-based data-quality report."""
    blank_rows = "\n".join(
        f"| `{column}` | {count} |"
        for column, count in audit["blank_cells_by_column"].items()
        if count
    ) or "| None | 0 |"
    checks = "\n".join(
        f"| `{name}` | {'PASS' if passed else 'FAIL'} |"
        for name, passed in summary["checks"].items()
    )
    return f"""# Data-quality report

Generated by `python src/data_pipeline.py` from the immutable raw CSV.

## Source structure

- Rows: {audit['rows']:,}
- Columns: {audit['columns']}
- Exact duplicate rows: {audit['duplicate_rows']}
- Duplicate customer IDs: {audit['duplicate_customer_ids']}
- Blank customer IDs: {audit['blank_customer_ids']}
- Records dropped during cleaning: {summary['records_dropped']}

## Blank source values

| Column | Blank values |
|---|---:|
{blank_rows}

Blank `TotalCharges` values are preserved as missing values. They are not changed to zero because the source does not establish that a blank balance means zero.
All such rows have zero recorded tenure, which is consistent with newly started accounts, but this association still does not prove that the missing charge should be replaced with zero.

## Numeric source audit

| Column | Failed conversions or blanks | Minimum | Maximum |
|---|---:|---:|---:|
| `SeniorCitizen` | {audit['numeric_audit']['SeniorCitizen']['conversion_failures_or_blanks']} | {audit['numeric_audit']['SeniorCitizen']['minimum']} | {audit['numeric_audit']['SeniorCitizen']['maximum']} |
| `tenure` | {audit['numeric_audit']['tenure']['conversion_failures_or_blanks']} | {audit['numeric_audit']['tenure']['minimum']} | {audit['numeric_audit']['tenure']['maximum']} |
| `MonthlyCharges` | {audit['numeric_audit']['MonthlyCharges']['conversion_failures_or_blanks']} | {audit['numeric_audit']['MonthlyCharges']['minimum']} | {audit['numeric_audit']['MonthlyCharges']['maximum']} |
| `TotalCharges` | {audit['numeric_audit']['TotalCharges']['conversion_failures_or_blanks']} | {audit['numeric_audit']['TotalCharges']['minimum']} | {audit['numeric_audit']['TotalCharges']['maximum']} |

## Transformations

1. Selected and ordered the 21 expected source fields; schema drift fails visibly.
2. Trimmed leading and trailing whitespace from text fields.
3. Converted empty strings to explicit missing values.
4. Renamed fields to consistent `snake_case` names.
5. Converted `senior_citizen` and `tenure` to nullable integers.
6. Converted `monthly_charges` and `total_charges` to nullable decimal numbers.
7. Preserved source service states such as `No`, `No internet service`, and `No phone service` as different categories.
8. Added `senior_citizen_label`, `churn_flag`, `total_charges_missing`, and a documented `tenure_band`.
9. Dropped no records.

Tenure bands are `0-12`, `13-24`, `25-48`, `49-60`, and `61-72` months. They provide ordered, understandable lifecycle groups and do not replace the original numeric tenure field.

## Validation results

| Check | Result |
|---|---|
{checks}

Overall status: **{summary['status']}**

## Unresolved issue

The original download URL and license/terms note were not supplied. They must be confirmed before portfolio publication. This does not prevent local analysis of the user-supplied file.
"""


def run_pipeline() -> dict[str, Any]:
    """Execute the repeatable Phase 2 pipeline and write governed outputs."""
    raw = load_raw()
    audit = audit_raw(raw)
    clean = clean_customer_data(raw)
    summary = validate(raw, clean, audit)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED_PATH, index=False, lineterminator="\n")
    summary["processed_sha256"] = file_sha256(PROCESSED_PATH)
    VALIDATION_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    QUALITY_REPORT_PATH.write_text(render_quality_report(audit, summary), encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = run_pipeline()
    print(json.dumps(result, indent=2))
