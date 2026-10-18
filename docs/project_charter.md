# Project charter

## Objective

Build a customer churn intelligence system that helps a telecom retention team understand who churns, where churn is concentrated, which observable factors are associated with churn, and which meaningful segments should be investigated first.

## Primary decision supported

Prioritize segments and questions for retention investigation and controlled experimentation without presenting observational associations as causal effects.

## Audience

- Retention or customer-success manager
- Commercial or marketing analyst
- Analytics portfolio reviewer

## Core business questions

1. What are the customer population, churn count, retained count, and churn rate?
2. How does churn vary across contract, tenure, internet service, payment method, paperless billing, and customer profile?
3. Which segments combine meaningful customer volume with elevated churn?
4. How do tenure, monthly charges, and total charges differ between churned and retained customers?
5. Which retention hypotheses follow from the evidence, and what new data or experiment could test them?

## In scope

- Data-quality audit and repeatable cleaning
- SQLite KPI and segmentation analysis
- Python exploratory analysis and documented visuals
- Power BI and Tableau reports
- Cross-tool reconciliation
- Executive narrative, limitations, README, and interview preparation

## Out of scope

- Causal conclusions from observational data
- Production deployment or real-time scoring
- Automated retention actions
- Complex machine learning
- Claims of business impact not measured by this project

## Provisional data contract

- Grain: one record per customer, subject to Phase 2 verification
- Candidate key: `customerID`, subject to uniqueness and null checks
- Target: `Churn`, subject to allowed-value and missingness checks
- Customer KPIs: distinct-customer counts where joins or duplicates could occur
- Churn-rate denominator: eligible distinct customers in the current filter context

## Definition of done

- Raw data is preserved and processed data is reproducible.
- Every KPI has a documented definition and reconciliation test.
- SQLite and Python agree on governed KPIs.
- Power BI and Tableau agree with the KPI reference.
- Every reported claim is traceable to evidence and includes an appropriate caveat.
- A clean-start run reproduces the main analytical outputs.
- The learner can explain and rebuild the required core components without copying.
