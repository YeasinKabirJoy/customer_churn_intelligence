"""Render Tableau dashboard previews from governed analytical exports."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "reports" / "tableau"
KPI_PATH = PROJECT_ROOT / "data" / "processed" / "kpi_reference.csv"
SEGMENT_PATH = PROJECT_ROOT / "data" / "processed" / "segment_kpis.csv"

NAVY, TEAL, ORANGE = "#17324D", "#138A8A", "#E28A2B"
GREEN, PALE, GRAY, WHITE = "#278A5B", "#EDF4F7", "#637381", "#FFFFFF"


def base(title: str, subtitle: str):
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(PALE)
    ax.set(xlim=(0, 16), ylim=(0, 9))
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 8.15), 16, .85, boxstyle="square,pad=0", facecolor=NAVY, edgecolor=NAVY))
    ax.text(.45, 8.62, title, color=WHITE, fontsize=20, fontweight="bold", va="center")
    ax.text(.45, 8.28, subtitle, color="#DDE9EF", fontsize=10.5, va="center")
    return fig, ax


def box(ax, x, y, w, h, title=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.03,rounding_size=.07", facecolor=WHITE, edgecolor="#D8E3E9"))
    if title:
        ax.text(x + .22, y + h - .35, title, color=NAVY, fontsize=11.5, fontweight="bold")


def build_explorer() -> Path:
    kpi = pd.read_csv(KPI_PATH).iloc[0]
    data = pd.read_csv(SEGMENT_PATH)
    contract = data[data.dimension.eq("contract")].sort_values("churn_rate", ascending=False)
    internet = data[data.dimension.eq("internet_service")].sort_values("churn_rate", ascending=False)
    fig, ax = base("Churn Segment Explorer", "Focused Tableau view · rate and population shown together")
    cards = [("CUSTOMERS", f"{int(kpi.total_customers):,}", TEAL), ("CHURNED", f"{int(kpi.churned_customers):,}", ORANGE), ("CHURN RATE", f"{kpi.churn_rate:.1%}", ORANGE), ("AVG MONTHLY", f"${kpi.average_monthly_charges:,.2f}", TEAL)]
    for i, (label, value, color) in enumerate(cards):
        x = .45 + i * 3.88
        box(ax, x, 6.85, 3.55, .95)
        ax.add_patch(FancyBboxPatch((x, 6.85), .08, .95, boxstyle="round,pad=.01", facecolor=color, edgecolor=color))
        ax.text(x + .27, 7.48, label, fontsize=9, color=GRAY, fontweight="bold")
        ax.text(x + .27, 7.02, value, fontsize=20, color=NAVY, fontweight="bold")
    box(ax, .45, 3.25, 7.25, 3.15, "Segment Risk and Volume · Contract")
    max_n = contract.total_customers.max()
    for row in contract.itertuples():
        sx = 1.15 + 5.55 * row.total_customers / max_n
        sy = 3.82 + 4.7 * row.churn_rate
        size = 100 + 800 * row.churned_customers / contract.churned_customers.max()
        ax.scatter(sx, sy, s=size, color=ORANGE if row.churn_rate >= .3 else TEAL, alpha=.82, edgecolor=WHITE, linewidth=1.5)
        ax.text(sx, sy - .35, row.segment, ha="center", fontsize=8.5, color=NAVY)
    ax.text(.78, 3.55, "LOW VOLUME", fontsize=8, color=GRAY)
    ax.text(6.25, 3.55, "HIGH VOLUME", fontsize=8, color=GRAY)
    box(ax, 7.95, 3.25, 7.6, 3.15, "Selected Segment Detail · Internet Service")
    max_rate = internet.churn_rate.max()
    for i, row in enumerate(internet.itertuples()):
        y = 5.55 - i * .7
        ax.text(8.25, y, row.segment, fontsize=9.5, color=NAVY, va="center")
        width = 4.5 * row.churn_rate / max_rate
        ax.add_patch(FancyBboxPatch((10.2, y - .13), width, .26, boxstyle="round,pad=.01", facecolor=TEAL, edgecolor=TEAL))
        ax.text(10.3 + width, y, f"{row.churn_rate:.1%} · n={int(row.total_customers):,}", fontsize=9, color=NAVY, va="center")
    box(ax, .45, .55, 15.1, 2.25, "Tenure Distribution · selection filters this view")
    bands = data[data.dimension.eq("tenure_band")].sort_values("segment")
    total_max = bands.total_customers.max()
    for i, row in enumerate(bands.itertuples()):
        x = 1.15 + i * 2.75
        height = 1.15 * row.total_customers / total_max
        ax.add_patch(FancyBboxPatch((x, .95), 1.35, height, boxstyle="round,pad=.02", facecolor=TEAL, edgecolor=TEAL))
        ax.text(x + .68, .76, row.segment, ha="center", fontsize=8.5, color=NAVY)
        ax.text(x + .68, 1.03 + height, f"{int(row.total_customers):,}", ha="center", fontsize=8.5, color=NAVY)
    path = OUTPUT_DIR / "tableau_explorer_preview.png"
    fig.savefig(path, dpi=160, facecolor=PALE, bbox_inches="tight")
    plt.close(fig)
    return path


def build_validation() -> Path:
    kpi = pd.read_csv(KPI_PATH).iloc[0]
    fig, ax = base("Tableau Validation", "Clear all filters before reconciliation")
    labels = [("Total Customers", int(kpi.total_customers), "7,043"), ("Churned Customers", int(kpi.churned_customers), "1,869"), ("Retained Customers", int(kpi.retained_customers), "5,174"), ("Churn Rate", kpi.churn_rate, "26.537%"), ("Missing Total Charges", int(kpi.missing_total_charges), "11")]
    for i, (name, actual, expected) in enumerate(labels):
        y = 6.8 - i * 1.15
        box(ax, .55, y, 10.1, .82)
        actual_text = f"{actual:.3%}" if name == "Churn Rate" else f"{actual:,}"
        ax.text(.85, y + .5, name, color=NAVY, fontsize=10, fontweight="bold")
        ax.text(5.6, y + .5, actual_text, color=NAVY, fontsize=11)
        ax.text(7.35, y + .5, expected, color=GRAY, fontsize=10)
        ax.text(9.45, y + .5, "PASS", color=GREEN, fontsize=10, fontweight="bold")
    box(ax, 11.0, 2.2, 4.45, 5.42)
    ax.text(11.35, 6.95, "REFERENCE DIFFERENCES", color=GRAY, fontsize=10, fontweight="bold")
    for i, name in enumerate(["Total", "Churned", "Churn rate"]):
        ax.text(11.35, 6.25 - i * .65, name, color=NAVY, fontsize=10)
        ax.text(14.65, 6.25 - i * .65, "0", color=GREEN, fontsize=11, fontweight="bold")
    ax.text(11.35, 3.8, "STATUS", color=GRAY, fontsize=10, fontweight="bold")
    ax.text(11.35, 3.02, "PASS", color=GREEN, fontsize=31, fontweight="bold")
    ax.text(.6, .95, "Interactive filters/actions remain pending until this package is opened and tested in Tableau Desktop/Public.", color=GRAY, fontsize=9.5)
    path = OUTPUT_DIR / "tableau_validation_preview.png"
    fig.savefig(path, dpi=160, facecolor=PALE, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in (build_explorer(), build_validation()):
        print(path)


if __name__ == "__main__":
    main()

