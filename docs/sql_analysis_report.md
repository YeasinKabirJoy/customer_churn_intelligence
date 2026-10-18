# Governed SQL analysis report

All values in this report come from the SQLite query pack and reconcile with an independent pandas calculation. Rates use distinct eligible customers in the relevant filter context.

## Overall KPI reference

| KPI | Verified value |
|---|---:|
| Total customers | 7,043 |
| Churned customers | 1,869 |
| Retained customers | 5,174 |
| Churn rate | 26.537% |
| Total monthly charges | 456,116.60 |
| Average monthly charges | 64.76 |
| Missing total-charge values | 11 |

`Total monthly charges` is the sum of the source `MonthlyCharges` field in the current customer snapshot. It is not labeled realized revenue because the dataset does not establish billing collection, timing, refunds, or accounting recognition.

## Verified segment associations

### Contract

| Contract | Customers | Churned | Churn rate |
|---|---:|---:|---:|
| Month-to-month | 3,875 | 1,655 | 42.710% |
| One year | 1,473 | 166 | 11.270% |
| Two year | 1,695 | 48 | 2.832% |

Evidence: month-to-month customers have the highest observed contract-level churn rate and represent 1,655 of the 1,869 churned customers.

Interpretation: contract structure is strongly associated with churn in this snapshot.

Caveat: customers are not randomly assigned to contracts. Tenure, pricing, preferences, promotions, and service experience may differ across contract groups.

### Tenure band

| Tenure band | Customers | Churned | Churn rate |
|---|---:|---:|---:|
| 0-12 months | 2,186 | 1,037 | 47.438% |
| 13-24 months | 1,024 | 294 | 28.711% |
| 25-48 months | 1,594 | 325 | 20.389% |
| 49-60 months | 832 | 120 | 14.423% |
| 61-72 months | 1,407 | 93 | 6.610% |

Evidence: observed churn rate decreases across the ordered tenure bands, and the first-year group contributes 1,037 churned customers.

Interpretation: early-lifecycle retention deserves investigation.

Caveat: this is a snapshot relationship and may partly reflect survivor selection—customers who remain necessarily accumulate tenure.

### Internet service

| Internet service | Customers | Churned | Churn rate |
|---|---:|---:|---:|
| Fiber optic | 3,096 | 1,297 | 41.893% |
| DSL | 2,421 | 459 | 18.959% |
| No internet service | 1,526 | 113 | 7.405% |

Evidence: the fiber-optic group has the highest observed churn rate and the largest churned-customer count among internet-service groups.

Interpretation: the fiber-optic customer experience, pricing, or customer mix warrants deeper analysis.

Caveat: the dataset cannot establish which of those possible explanations is responsible.

### Payment method

| Payment method | Customers | Churned | Churn rate |
|---|---:|---:|---:|
| Electronic check | 2,365 | 1,071 | 45.285% |
| Mailed check | 1,612 | 308 | 19.107% |
| Bank transfer (automatic) | 1,544 | 258 | 16.710% |
| Credit card (automatic) | 1,522 | 232 | 15.243% |

Evidence: electronic-check customers have the highest observed payment-method churn rate and account for 1,071 churned customers.

Interpretation: payment friction, self-selection, or correlated contract/customer characteristics should be investigated.

Caveat: changing payment method alone cannot be assumed to reduce churn.

## Charge context

| Churn | Customers | Average monthly charges | Customers with total charges | Average total charges |
|---|---:|---:|---:|---:|
| No | 5,174 | 61.27 | 5,163 | 2,555.34 |
| Yes | 1,869 | 74.44 | 1,869 | 1,531.80 |

Churned customers have higher average monthly charges but lower average total charges in this snapshot. The lower total-charge average is consistent with the observed concentration of churn among shorter-tenure customers, because total charges accumulate over time. Distribution checks are required in Phase 4 before turning this comparison into a polished insight.

## Reconciliation evidence

- Churned plus retained customers equals total customers.
- Customer IDs are unique in SQLite.
- For each of nine segmentation dimensions, segment customer totals equal 7,043.
- For each dimension, segment churned totals equal 1,869.
- SQL and independent pandas KPI calculations agree within `1e-12` for rates and normal floating-point tolerance for charge aggregates.

## Appropriate action hypotheses

These are hypotheses for investigation, not measured impact claims:

1. Investigate early-tenure onboarding and service-resolution experiences.
2. Examine whether fiber-optic pricing, reliability, support contacts, or customer mix explains its elevated observed churn.
3. Test whether payment-method friction or correlated contract characteristics explain the electronic-check pattern.
4. Design controlled retention experiments only after defining treatment eligibility, success metrics, guardrails, and a comparison group.
