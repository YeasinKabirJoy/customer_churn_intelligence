"""Render the final Power BI Predictive Demonstration page preview."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
ML_DIR = ROOT / "reports" / "ml"
OUTPUT = ROOT / "reports" / "powerbi" / "predictive_demonstration_preview.png"
NAVY, TEAL, ORANGE, PALE, GRAY, WHITE = "#17324D", "#138A8A", "#E28A2B", "#EDF4F7", "#637381", "#FFFFFF"


def box(ax, x, y, w, h, color=WHITE, edge="#D8E3E9"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.03,rounding_size=.07", facecolor=color, edgecolor=edge))


def main() -> Path:
    metrics = pd.read_csv(ML_DIR / "model_metrics.csv").set_index("model").loc["logistic_regression"]
    deciles = pd.read_csv(ML_DIR / "risk_deciles.csv")
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor(PALE)
    ax.set(xlim=(0, 16), ylim=(0, 9)); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 8.12), 16, .88, boxstyle="square,pad=0", facecolor=NAVY, edgecolor=NAVY))
    ax.text(.45, 8.62, "Predictive Demonstration", color=WHITE, fontsize=20, fontweight="bold", va="center")
    ax.text(.45, 8.27, "Held-out evaluation · Logistic regression · Proof of concept", color="#DDE9EF", fontsize=10.5, va="center")
    cards = [("ROC-AUC", f"{metrics.roc_auc:.3f}"), ("AVERAGE PRECISION", f"{metrics.average_precision:.3f}"), ("CHURNERS CAPTURED", f"{int(metrics.churners_captured_top_20_percent)}"), ("TOP-20% RECALL", f"{metrics.recall_at_top_20_percent:.1%}"), ("LIFT", f"{metrics.lift_at_top_20_percent:.2f}×")]
    for i, (label, value) in enumerate(cards):
        x = .45 + i * 3.08; box(ax, x, 6.85, 2.75, .95)
        ax.text(x + .2, 7.47, label, fontsize=8.5, color=GRAY, fontweight="bold")
        ax.text(x + .2, 7.02, value, fontsize=19, color=NAVY, fontweight="bold")
    box(ax, .45, 3.05, 9.2, 3.35)
    ax.text(.7, 6.05, "Observed churn by predicted-risk decile", color=NAVY, fontsize=12, fontweight="bold")
    xs = [1.1 + i * .78 for i in range(10)]
    for x, row in zip(xs, deciles.itertuples()):
        height = 2.15 * row.actual_churn_rate / deciles.actual_churn_rate.max()
        ax.add_patch(FancyBboxPatch((x, 3.65), .48, height, boxstyle="round,pad=.01", facecolor=TEAL, edgecolor=TEAL))
        ax.text(x + .24, 3.4, str(int(row.risk_decile)), ha="center", fontsize=8.5, color=NAVY)
    line_y = 3.65 + 2.15 * deciles.average_predicted_risk / deciles.actual_churn_rate.max()
    ax.plot([x + .24 for x in xs], line_y, color=ORANGE, marker="o", linewidth=2)
    ax.text(1.0, 3.15, "1 = highest risk", fontsize=8.5, color=GRAY)
    box(ax, 9.9, 3.05, 5.65, 3.35)
    ax.text(10.2, 6.05, "Confusion matrix · threshold 0.5", color=NAVY, fontsize=12, fontweight="bold")
    for r, row in enumerate([[918, 117], [171, 203]]):
        for c, value in enumerate(row):
            x, y = 11.2 + c * 1.45, 4.85 - r * 1.05
            ax.add_patch(FancyBboxPatch((x, y), 1.2, .8, boxstyle="round,pad=.02", facecolor="#5687B5" if value > 500 else "#BFD6EA", edgecolor=WHITE))
            ax.text(x + .6, y + .4, f"{value:,}", ha="center", va="center", fontsize=12, color=NAVY, fontweight="bold")
    ax.text(11.8, 5.82, "Predicted", ha="center", fontsize=8.5, color=GRAY)
    ax.text(10.35, 4.55, "Actual", rotation=90, va="center", fontsize=8.5, color=GRAY)
    box(ax, .45, 1.45, 7.35, 1.2, color="#F0FAF5", edge="#9CCDB4")
    ax.text(.7, 2.3, "HYPOTHETICAL CONTACT CAPACITY", fontsize=9, color=GRAY, fontweight="bold")
    ax.text(.7, 1.82, "Top 282 test customers capture 184 of 374 churners (49.2%; 2.46× lift).", fontsize=10.5, color=NAVY)
    box(ax, 8.05, 1.45, 7.5, 1.2, color="#FFF7ED", edge="#F0C98B")
    ax.text(8.3, 2.3, "MODEL LIMITATIONS", fontsize=9, color=GRAY, fontweight="bold")
    ax.text(8.3, 1.87, "Static snapshot · no temporal validation · associations are not causal", fontsize=9.5, color=NAVY)
    ax.text(8.3, 1.58, "Threshold economics, fairness governance, and monitoring remain required.", fontsize=9.5, color=NAVY)
    ax.add_patch(FancyBboxPatch((.45, .42), 15.1, .62, boxstyle="round,pad=.02", facecolor="#FFF0E0", edgecolor=ORANGE))
    ax.text(.72, .73, "PROOF OF CONCEPT — NOT FOR AUTOMATED CUSTOMER DECISIONS", color=ORANGE, fontsize=10.5, fontweight="bold", va="center")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=160, facecolor=PALE, bbox_inches="tight"); plt.close(fig)
    print(OUTPUT); return OUTPUT


if __name__ == "__main__":
    main()

