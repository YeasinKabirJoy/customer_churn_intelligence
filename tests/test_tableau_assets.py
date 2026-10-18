"""Validate Tableau source assets and static previews."""

from pathlib import Path

from src.tableau_preview import OUTPUT_DIR, main

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_calculated_fields_cover_governed_kpis() -> None:
    text = (OUTPUT_DIR / "calculated_fields.txt").read_text(encoding="utf-8")
    for name in ["Total Customers", "Churned Customers", "Retained Customers", "Churn Rate", "Total Monthly Charges", "Average Monthly Charges", "Missing Total Charges"]:
        assert name in text
    assert "COUNTD([customer_id])" in text
    assert "Reference Churn Rate Difference" in text


def test_dashboard_specification_has_required_interactions() -> None:
    text = (OUTPUT_DIR / "dashboard_specification.md").read_text(encoding="utf-8")
    assert "Dashboard action" in text
    assert "Clearing the selection restores all customers" in text
    assert "all differences must be zero" in text


def test_tableau_previews_render() -> None:
    main()
    for filename in ["tableau_explorer_preview.png", "tableau_validation_preview.png"]:
        assert (OUTPUT_DIR / filename).stat().st_size > 0

