# Executive brief

The sample contains 7,043 customers and 1,869 observed churners, producing a 26.537% churn rate. The most defensible next step is to investigate and experimentally test improvements in the early customer lifecycle, especially among month-to-month and fiber-optic customers, rather than launch an untargeted discount campaign.

## Verified evidence

- Month-to-month: 3,875 customers, 1,655 churned, 42.7% churn.
- First 0–12 months: 2,186 customers, 1,037 churned, 47.4% churn.
- Fiber optic: 3,096 customers, 1,297 churned, 41.9% churn.
- Electronic check: 2,365 customers, 1,071 churned, 45.3% churn.
- Median monthly charges: 79.65 for churned versus 64.43 for retained customers.
- Median tenure: 10 months for churned versus 38 months for retained customers.

These are overlapping characteristics, so their counts must not be added as separate opportunities.

## Recommended action and experiment

Diagnose onboarding and service experience during months 0–12 using support, outage, installation, promotion, and satisfaction data. Randomize eligible early-tenure, month-to-month customers into control and treatment groups. Test a service-oriented intervention before broad discounts. Measure future-window churn, experience guardrails, and cost; report intention-to-treat lift.

Investigate fiber pricing and service quality before selecting an intervention, review electronic-check journeys for friction while controlling for contract and tenure, and use modeled risk only to prioritize a controlled test—not automate treatment.

## Predictive evidence and limitations

Logistic regression achieved 0.839 ROC-AUC and 0.630 average precision on 1,409 held-out customers. The highest-risk 20% captured 184 of 374 test churners, or 49.2%, with 2.46× lift. This is same-population holdout evidence, not future-period or causal evidence.

The public data is a static observational snapshot without timestamps, service-quality events, support interactions, promotions, customer value, intervention outcomes, or a future outcome window. Production use requires temporal validation, economics, governance, monitoring, and experimentation.

