"""Final portfolio packaging and predictive dashboard tests."""
from pathlib import Path
from src.ml_dashboard_preview import OUTPUT, main

ROOT = Path(__file__).resolve().parents[1]


def test_predictive_dashboard_contract_contains_required_metrics() -> None:
    dax = (ROOT / "reports" / "powerbi" / "ml_measures.dax").read_text(encoding="utf-8")
    spec = (ROOT / "reports" / "powerbi" / "ml_dashboard_specification.md").read_text(encoding="utf-8")
    for phrase in ["ML ROC AUC", "ML Average Precision", "ML Recall at Top 20", "ML True Positives"]:
        assert phrase in dax
    for phrase in ["0.839", "0.630", "184", "PROOF OF CONCEPT"]:
        assert phrase in spec


def test_final_portfolio_documents_exist() -> None:
    for name in ["executive_brief.md", "cross_tool_reconciliation.md", "reproducibility_runbook.md", "portfolio_release_checklist.md", "complete_interview_guide.md"]:
        assert (ROOT / "docs" / name).stat().st_size > 0


def test_complete_interview_guide_has_full_question_set() -> None:
    guide = (ROOT / "docs" / "complete_interview_guide.md").read_text(encoding="utf-8")
    assert "### 1." in guide
    assert "### 155." in guide
    assert "## 15-day beginner-to-intermediate study plan" in guide
    assert "STAR — Situation, Task, Action, Result" in guide
    for expansion in ["Business Intelligence", "Structured Query Language", "Exploratory Data Analysis", "Data Analysis Expressions", "Receiver Operating Characteristic"]:
        assert expansion in guide


def test_predictive_dashboard_preview_renders() -> None:
    main(); assert OUTPUT.stat().st_size > 0

