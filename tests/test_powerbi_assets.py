"""Static validation for Power BI source assets and previews."""

from __future__ import annotations

import json
from pathlib import Path

from src.powerbi_preview import OUTPUT_DIR, main


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_theme_is_valid_json_with_governed_colors() -> None:
    theme = json.loads((OUTPUT_DIR / "theme.json").read_text(encoding="utf-8"))
    assert theme["name"] == "Telecom Churn Intelligence"
    assert "#138A8A" in theme["dataColors"]
    assert "#E28A2B" in theme["dataColors"]


def test_dax_contains_all_governed_measures() -> None:
    dax = (OUTPUT_DIR / "measures.dax").read_text(encoding="utf-8")
    for measure in [
        "Total Customers",
        "Churned Customers",
        "Retained Customers",
        "Churn Rate",
        "Total Monthly Charges",
        "Average Monthly Charges",
        "Missing Total Charges",
    ]:
        assert f"{measure} =" in dax
    assert "DISTINCTCOUNT" in dax
    assert "CALCULATE" in dax
    assert "DIVIDE" in dax


def test_tmdl_contains_model_partition_and_measures() -> None:
    tmdl = (OUTPUT_DIR / "model.tmdl").read_text(encoding="utf-8")
    assert tmdl.startswith("createOrReplace")
    assert "partition telco_customer_churn_clean = m" in tmdl
    assert "measure 'Churn Rate'" in tmdl
    assert "File.Contents" in tmdl


def test_preview_pages_render() -> None:
    main()
    for filename in [
        "executive_overview_preview.png",
        "segment_explorer_preview.png",
        "validation_page_preview.png",
    ]:
        assert (OUTPUT_DIR / filename).stat().st_size > 0
