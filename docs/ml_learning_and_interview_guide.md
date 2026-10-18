# ML learning and interview guide

## Project explanation

I added a lightweight predictive layer after completing descriptive and diagnostic analysis. Logistic regression is the primary risk-ranking model because its probabilities and feature associations are explainable. A depth-four decision tree is a comparison model that captures simple nonlinear rules. Both models use the same stratified 80/20 split and training-only preprocessing.

## Questions and model answers

**Why not optimize accuracy?** Churn is the minority class. A model predicting retention for everyone could look accurate while finding no churners. I report ROC-AUC, average precision, precision, recall, F1, calibration error, lift, and recall at a 20% contact capacity.

**Why a pipeline?** The pipeline fits imputation, scaling, and category encoding only on training data. This prevents information from the test set leaking into preprocessing.

**Why stratify the split?** Stratification keeps approximately the same churn prevalence in train and test sets, producing a more stable comparison.

**Why logistic regression?** It is a strong, understandable baseline that ranks risk, supports probability outputs, and exposes coefficient direction. Coefficients are associations conditional on the encoded inputs, not causal effects.

**Why a shallow tree?** It demonstrates nonlinear decision rules without creating an opaque or heavily overfit model. The constraints are intentionally conservative.

**Why exclude Total Charges?** It is largely accumulated tenure multiplied by charges, contains missing values, and can dominate as a lifecycle proxy. Tenure and monthly charges retain the core information more transparently for this initial model.

**What is leakage?** Leakage occurs when training uses information that would not be available at prediction time or indirectly contains the target. Customer ID, churn labels, outcome-derived fields, and test-fitted transformations are excluded.

**What does ROC-AUC mean?** It is the probability that a randomly selected churner receives a higher score than a randomly selected retained customer. It measures ranking across thresholds, not operational value at one threshold.

**Why average precision?** It summarizes the precision-recall tradeoff and is more informative than accuracy when the positive class is less common.

**What is lift at 20%?** It compares the churn rate among the highest-risk 20% with the overall test churn rate. It answers whether limited retention capacity is concentrated on a richer set of churners.

**Why inspect fairness slices?** Aggregate performance can hide unequal recall or selection rates. Gender and senior-citizen slices are diagnostic checks, not proof of fairness; deployment would require policy, legal, sample-size, and harm reviews.

**What prevents production use?** The dataset lacks timestamps, observation windows, intervention outcomes, population drift evidence, and a deployment context. Production work requires temporal validation, leakage review, calibration, threshold economics, fairness review, monitoring, security, and controlled retention experiments.

