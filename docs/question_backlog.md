# Question backlog

## Data and provenance

- What is the original download URL and license/terms note?
- Does the actual file prove one row per customer?
- Are identifiers complete and unique?
- Which columns contain blanks, nulls, inconsistent labels, or invalid ranges?
- Does `TotalCharges` require numeric coercion, and what business situation explains any blank values?

## KPI governance

- Which rows qualify for the churn-rate denominator?
- How should missing or unexpected churn values be handled?
- Is “monthly revenue” an approved name for the sum of `MonthlyCharges`, or should it retain a more cautious label?
- What reconciliation tolerance and rounding policy should all tools use?
- What tenure-band boundaries are analytically useful and easy to explain?

## Analysis

- Which segments combine substantial customer volume with elevated churn?
- Do average-charge comparisons hide important distribution differences?
- Which findings remain stable after accounting for segment size?
- Which additional variables would be needed to test the most useful retention hypotheses?

## Delivery

- Should Power BI and Tableau connect to the SQLite database or governed exported tables?
- Which final screen size should guide dashboard layout testing?
- What fallback exports are needed for reviewers without the desktop BI applications?
