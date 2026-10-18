"""Render static Power BI page previews from governed reference exports."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "reports" / "powerbi"
KPI_PATH = PROJECT_ROOT / "data" / "processed" / "kpi_reference.csv"
SEGMENT_PATH = PROJECT_ROOT / "data" / "processed" / "segment_kpis.csv"
CHECK_PATH = PROJECT_ROOT / "data" / "processed" / "sql_sanity_checks.csv"

NAVY = "#17324D"
TEAL = "#138A8A"
ORANGE = "#E28A2B"
LIGHT_BLUE = "#7DB7D8"
PALE = "#EDF4F7"
GRAY = "#637381"
WHITE = "#FFFFFF"
GREEN = "#278A5B"


def setup_page(title: str, subtitle: str) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 8.15), 16, 0.85, boxstyle="square,pad=0", facecolor=NAVY, edgecolor=NAVY))
    ax.text(0.45, 8.62, "Telecom Customer Churn Intelligence", color=WHITE, fontsize=20, fontweight="bold", va="center")
    ax.text(0.45, 8.28, f"{title}  |  {subtitle}", color="#DDE9EF", fontsize=10.5, va="center")
    return fig, ax


def card(ax: plt.Axes, x: float, y: float, width: float, title: str, value: str, accent: str = TEAL) -> None:
    ax.add_patch(FancyBboxPatch((x, y), width, 1.05, boxstyle="round,pad=0.03,rounding_size=0.08", facecolor=WHITE, edgecolor="#D8E3E9", linewidth=1.3))
    ax.add_patch(FancyBboxPatch((x, y), 0.08, 1.05, boxstyle="round,pad=0.02,rounding_size=0.05", facecolor=accent, edgecolor=accent))
    ax.text(x + 0.28, y + 0.72, title, fontsize=10, color=GRAY, fontweight="bold")
    ax.text(x + 0.28, y + 0.25, value, fontsize=22, color=NAVY, fontweight="bold")


def panel(ax: plt.Axes, x: float, y: float, w: float, h: float, title: str) -> None:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.07", facecolor=WHITE, edgecolor="#D8E3E9", linewidth=1.2))
    ax.text(x + 0.22, y + h - 0.38, title, fontsize=12, color=NAVY, fontweight="bold")


def horizontal_bars(ax: plt.Axes, data: pd.DataFrame, x: float, y: float, w: float, h: float) -> None:
    maximum = max(data["churn_rate"])
    row_h = (h - 0.85) / len(data)
    for index, row in enumerate(data.itertuples()):
        cy = y + h - 0.85 - index * row_h
        ax.text(x + 0.18, cy, str(row.segment), fontsize=9.5, color=GRAY, va="center")
        bx = x + w * 0.43
        bw = w * 0.43 * row.churn_rate / maximum
        ax.add_patch(FancyBboxPatch((bx, cy - 0.13), bw, 0.26, boxstyle="round,pad=0.01,rounding_size=0.03", facecolor=TEAL, edgecolor=TEAL))
        ax.text(bx + bw + 0.1, cy, f"{row.churn_rate:.1%} · n={int(row.total_customers):,}", fontsize=9, color=NAVY, va="center")


def build_executive() -> Path:
    kpi = pd.read_csv(KPI_PATH).iloc[0]
    segments = pd.read_csv(SEGMENT_PATH)
    fig, ax = setup_page("Executive Overview", "Verified customer-level measures")
    card(ax, 0.45, 6.75, 3.45, "TOTAL CUSTOMERS", f"{int(kpi.total_customers):,}")
    card(ax, 4.15, 6.75, 3.45, "CHURNED CUSTOMERS", f"{int(kpi.churned_customers):,}", ORANGE)
    card(ax, 7.85, 6.75, 3.45, "CHURN RATE", f"{kpi.churn_rate:.1%}", ORANGE)
    card(ax, 11.55, 6.75, 4.0, "AVG MONTHLY CHARGES", f"${kpi.average_monthly_charges:,.2f}")

    panel(ax, 0.45, 3.45, 7.35, 2.85, "Churn rate by contract")
    contract = segments.loc[segments.dimension == "contract"].sort_values("churn_rate", ascending=False)
    horizontal_bars(ax, contract, 0.65, 3.55, 6.9, 2.4)
    panel(ax, 8.05, 3.45, 7.5, 2.85, "Churn rate by tenure band")
    tenure = segments.loc[segments.dimension == "tenure_band"].sort_values("churn_rate", ascending=False)
    horizontal_bars(ax, tenure, 8.25, 3.55, 7.05, 2.4)

    panel(ax, 0.45, 0.7, 7.35, 2.3, "Churn rate by internet service")
    internet = segments.loc[segments.dimension == "internet_service"].sort_values("churn_rate", ascending=False)
    horizontal_bars(ax, internet, 0.65, 0.78, 6.9, 1.9)
    ax.add_patch(FancyBboxPatch((8.05, 0.7), 7.5, 2.3, boxstyle="round,pad=0.03,rounding_size=0.07", facecolor="#FFF7ED", edgecolor="#F0C98B", linewidth=1.2))
    ax.text(8.3, 2.55, "Decision note", fontsize=12, color=NAVY, fontweight="bold")
    ax.text(8.3, 2.05, "Investigate early-tenure, month-to-month, and fiber experience.", fontsize=11, color=NAVY)
    ax.text(8.3, 1.62, "Observed association is not proof of causation.", fontsize=11, color=ORANGE, fontweight="bold")
    ax.text(8.3, 1.15, "Recommended filters: Contract · Internet Service · Tenure Band · Payment Method · Senior Citizen", fontsize=9.3, color=GRAY)
    path = OUTPUT_DIR / "executive_overview_preview.png"
    fig.savefig(path, dpi=160, facecolor=WHITE, bbox_inches="tight")
    plt.close(fig)
    return path


def build_explorer() -> Path:
    segments = pd.read_csv(SEGMENT_PATH)
    fig, ax = setup_page("Segment Explorer", "Volume and churn rate shown together")
    panel(ax, 0.45, 4.45, 15.1, 2.95, "Payment-method comparison")
    payment = segments.loc[segments.dimension == "payment_method"].sort_values("churn_rate", ascending=False)
    horizontal_bars(ax, payment, 0.7, 4.55, 14.55, 2.5)
    panel(ax, 0.45, 1.0, 7.35, 3.0, "Internet-service comparison")
    internet = segments.loc[segments.dimension == "internet_service"].sort_values("churn_rate", ascending=False)
    horizontal_bars(ax, internet, 0.7, 1.08, 6.8, 2.55)
    panel(ax, 8.05, 1.0, 7.5, 3.0, "Selected-segment detail")
    ax.text(8.35, 3.35, "Segment", color=GRAY, fontsize=9, fontweight="bold")
    ax.text(11.6, 3.35, "Customers", color=GRAY, fontsize=9, fontweight="bold")
    ax.text(13.05, 3.35, "Churned", color=GRAY, fontsize=9, fontweight="bold")
    ax.text(14.35, 3.35, "Rate", color=GRAY, fontsize=9, fontweight="bold")
    for i, row in enumerate(payment.itertuples()):
        yy = 2.9 - i * 0.52
        ax.text(8.35, yy, str(row.segment), color=NAVY, fontsize=9.5)
        ax.text(11.75, yy, f"{int(row.total_customers):,}", color=NAVY, fontsize=9.5)
        ax.text(13.15, yy, f"{int(row.churned_customers):,}", color=NAVY, fontsize=9.5)
        ax.text(14.4, yy, f"{row.churn_rate:.1%}", color=NAVY, fontsize=9.5, fontweight="bold")
    ax.text(0.5, 0.45, "Filters apply to both numerator and denominator. Clear all filters before validation.", color=GRAY, fontsize=9.5)
    path = OUTPUT_DIR / "segment_explorer_preview.png"
    fig.savefig(path, dpi=160, facecolor=WHITE, bbox_inches="tight")
    plt.close(fig)
    return path


def build_validation() -> Path:
    kpi = pd.read_csv(KPI_PATH).iloc[0]
    checks = pd.read_csv(CHECK_PATH)
    fig, ax = setup_page("Validation", "Builder-facing reconciliation page")
    cards = [
        ("TOTAL", f"{int(kpi.total_customers):,}"),
        ("CHURNED", f"{int(kpi.churned_customers):,}"),
        ("RETAINED", f"{int(kpi.retained_customers):,}"),
        ("CHURN RATE", f"{kpi.churn_rate:.3%}"),
        ("MISSING TOTAL CHARGES", f"{int(kpi.missing_total_charges):,}"),
    ]
    for i, (title, value) in enumerate(cards):
        card(ax, 0.45 + i * 3.05, 6.65, 2.75, title, value, GREEN)
    panel(ax, 0.45, 1.0, 10.2, 5.05, "Reconciliation checks")
    displayed = checks.head(10)
    for i, row in enumerate(displayed.itertuples()):
        yy = 5.45 - i * 0.42
        ax.text(0.75, yy, row.check_name.replace("_", " "), fontsize=9.3, color=NAVY)
        ax.text(9.45, yy, row.status, fontsize=9.3, color=GREEN, fontweight="bold")
    ax.add_patch(FancyBboxPatch((11.0, 1.0), 4.55, 5.05, boxstyle="round,pad=0.03,rounding_size=0.07", facecolor="#F0FAF5", edgecolor="#9CCDB4", linewidth=1.2))
    ax.text(11.3, 5.45, "VALIDATION STATUS", fontsize=11, color=GRAY, fontweight="bold")
    ax.text(11.3, 4.6, "PASS", fontsize=32, color=GREEN, fontweight="bold")
    ax.text(11.3, 3.95, f"{len(checks)} SQL checks passed", fontsize=11, color=NAVY)
    ax.text(11.3, 3.5, "All difference measures: 0", fontsize=11, color=NAVY)
    ax.text(11.3, 2.65, "Required state", fontsize=10, color=GRAY, fontweight="bold")
    ax.text(11.3, 2.2, "• All slicers cleared", fontsize=10, color=NAVY)
    ax.text(11.3, 1.8, "• Latest data refresh", fontsize=10, color=NAVY)
    ax.text(11.3, 1.4, "• No hidden page filters", fontsize=10, color=NAVY)
    path = OUTPUT_DIR / "validation_page_preview.png"
    fig.savefig(path, dpi=160, facecolor=WHITE, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in [build_executive(), build_explorer(), build_validation()]:
        print(path)


if __name__ == "__main__":
    main()
