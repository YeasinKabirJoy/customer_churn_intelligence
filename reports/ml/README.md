# Phase 7 — lightweight churn prediction

This folder contains a reproducible proof-of-concept risk-ranking exercise. Logistic regression is the primary model; a deliberately shallow decision tree provides an interpretable comparison.

The models are not production-ready. The source is a static public snapshot without observation dates or a future outcome window, so the holdout estimates may not represent future performance.

Key outputs include model metrics, confusion/calibration diagnostics, ROC and precision-recall curves, risk deciles, logistic feature associations, fairness slices, saved model pipelines, and held-out dashboard prediction rows.

Run `python src/ml_pipeline.py`, then `python -m pytest`.

