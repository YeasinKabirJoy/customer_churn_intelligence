# Phase 7 held-out results

## Primary result

The logistic-regression model was evaluated on 1,409 held-out customers containing 374 churners. It achieved ROC-AUC 0.839, average precision 0.630, precision 0.634, recall 0.543, and F1 0.585 at the untuned 0.5 threshold. Its Brier score was 0.139.

At a hypothetical contact capacity of 20% of test customers, the model selected 282 customers and captured 184 churners: 49.2% of all test churners, with 2.46× lift over the test-set baseline churn rate.

The shallow decision tree achieved ROC-AUC 0.830 and average precision 0.601. Its slightly weaker ranking and calibration support retaining logistic regression as the primary proof-of-concept model.

## Interpretation

The risk deciles show useful separation: observed churn was 73.0% in the highest-risk decile and 1.4% in the lowest-risk decile. This supports risk ranking within the held-out sample; it does not establish future-period performance.

Large logistic associations included longer tenure and two-year contracts with lower modeled risk, and fiber-optic service and month-to-month contracts with higher modeled risk. Because encoded features are correlated and coefficients are conditional on the other inputs, individual coefficients must not be presented as causal effects.

## Fairness diagnostics

Selection rates at the top-20% policy were similar across the recorded gender categories: 19.8% for Female and 20.2% for Male in the test sample. They differed substantially by senior-citizen label: 16.7% for No and 37.8% for Yes, alongside different observed churn prevalence. This requires policy and harm review; it is not evidence that the system is fair or that age-related targeting is appropriate.

## Decision

The model is suitable for a portfolio demonstration and hypothetical experiment design. It is not suitable for automated retention decisions. A real deployment requires prediction timestamps, future outcome windows, temporal validation, economic threshold analysis, treatment-effect experimentation, fairness governance, calibration monitoring, and drift controls.
