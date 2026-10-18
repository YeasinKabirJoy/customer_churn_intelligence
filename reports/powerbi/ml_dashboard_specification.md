# Predictive Demonstration page

This page stays separate from descriptive dashboards. It reports fixed held-out evaluation results, not live predictions for all customers.

Import without relationships: `reports/ml/model_metrics.csv` as `ML Model Metrics`, `reports/ml/risk_deciles.csv` as `ML Risk Deciles`, and `data/processed/ml_test_predictions.csv` as `ML Test Predictions`. Create the measures in `ml_measures.dax`.

Layout: header **Predictive Demonstration**; KPI cards for ROC-AUC 0.839, average precision 0.630, churners captured 184, top-20% recall 49.2%, and lift 2.46×; risk-decile column/line chart; confusion matrix with TN 918, FP 117, FN 171, TP 203; capacity note; limitations panel; disclaimer.

> PROOF OF CONCEPT — NOT FOR AUTOMATED CUSTOMER DECISIONS. Results measure same-population holdout performance. Production use requires prediction timestamps, temporal validation, leakage review, threshold economics, fairness governance, security, monitoring, and controlled retention experiments.

