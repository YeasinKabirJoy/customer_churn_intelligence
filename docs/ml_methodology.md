# Phase 7 ML methodology

## Objective

Rank customers by observed churn risk as a portfolio proof of concept. The objective is not to claim future production performance or causal drivers.

## Design

- Target: `churn_flag`.
- Split: stratified 80% train / 20% held-out test, random seed 42.
- Primary model: logistic regression.
- Comparison: decision tree limited to depth 4 and at least 100 training observations per leaf.
- Numeric preprocessing: median imputation and standardization.
- Categorical preprocessing: most-frequent imputation and one-hot encoding with unknown-category handling.
- Threshold reporting: 0.5 for classification metrics.
- Capacity reporting: highest-risk 20% of the held-out test customers.

## Leakage controls

`customer_id`, `churn`, `churn_flag`, `total_charges`, `total_charges_missing`, `tenure_band`, and `senior_citizen_label` are not predictors. Preprocessing is fitted inside each training pipeline. The held-out test set is not used for model selection or threshold tuning.

## Known limitations

The dataset is a single snapshot without prediction timestamps. The random holdout therefore tests same-population generalization, not future-period performance. Feature associations are not causal effects. Fairness slices are descriptive diagnostics and do not certify equitable use.

