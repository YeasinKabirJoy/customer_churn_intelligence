"""Tests for row-preserving and deterministic customer-data cleaning."""

from __future__ import annotations

import pandas as pd

from src.data_pipeline import (
    EXPECTED_COLUMNS,
    TENURE_LABELS,
    audit_raw,
    clean_customer_data,
    load_raw,
    validate,
)


def test_source_schema_and_customer_grain() -> None:
    raw = load_raw()
    assert raw.columns.tolist() == EXPECTED_COLUMNS
    assert raw["customerID"].str.strip().ne("").all()
    assert raw["customerID"].is_unique


def test_cleaning_preserves_rows_and_customer_ids() -> None:
    raw = load_raw()
    clean = clean_customer_data(raw)
    assert len(clean) == len(raw)
    assert clean["customer_id"].tolist() == raw["customerID"].str.strip().tolist()


def test_total_charges_blanks_become_missing_not_zero() -> None:
    raw = load_raw()
    clean = clean_customer_data(raw)
    source_blank = raw["TotalCharges"].str.strip().eq("")
    assert (clean["total_charges"].isna().to_numpy() == source_blank.to_numpy()).all()
    assert clean.loc[source_blank, "total_charges"].isna().all()


def test_service_not_applicable_values_are_preserved() -> None:
    clean = clean_customer_data(load_raw())
    assert "No phone service" in set(clean["multiple_lines"])
    for column in [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]:
        assert "No internet service" in set(clean[column])


def test_derived_fields_are_complete_and_explainable() -> None:
    clean = clean_customer_data(load_raw())
    assert clean["churn_flag"].notna().all()
    assert clean["senior_citizen_label"].notna().all()
    assert clean["tenure_band"].notna().all()
    assert clean["tenure_band"].cat.categories.tolist() == TENURE_LABELS


def test_cleaning_is_deterministic() -> None:
    raw = load_raw()
    first = clean_customer_data(raw)
    second = clean_customer_data(raw)
    pd.testing.assert_frame_equal(first, second)


def test_all_critical_validations_pass() -> None:
    raw = load_raw()
    audit = audit_raw(raw)
    summary = validate(raw, clean_customer_data(raw), audit)
    assert summary["status"] == "PASS"
    assert all(summary["checks"].values())
