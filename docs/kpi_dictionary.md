# KPI dictionary

These definitions are frozen for SQLite, Python, Power BI, and Tableau unless a later documented decision explicitly revises them.

| KPI | Business meaning | Grain | Formula | Denominator / filter behavior | Null rule | Format | Reconciliation |
|---|---|---|---|---|---|---|---|
| Total Customers | Distinct eligible customers in the current context | Customer | `COUNT(DISTINCT customer_id)` | All customers remaining after active filters | `customer_id` cannot be null | Whole number | Must equal processed unique customer count with no filters |
| Churned Customers | Distinct eligible customers whose source outcome is `Yes` | Customer | Distinct customers where `churn_flag = 1` | Same active filter context as Total Customers | `churn_flag` cannot be null | Whole number | Must agree with independent pandas count |
| Retained Customers | Distinct eligible customers whose source outcome is `No` | Customer | Distinct customers where `churn_flag = 0` | Same active filter context as Total Customers | `churn_flag` cannot be null | Whole number | Churned + Retained must equal Total |
| Churn Rate | Share of eligible customers who churned | Customer | Churned Customers / Total Customers | Recomputed inside the current filter context; never average displayed segment rates | Safe division returns null for an empty denominator | Percentage, normally 1 decimal in dashboards; full precision retained for checks | SQL and pandas must match within `1e-12`; BI tools must match displayed rounding |
| Total Monthly Charges | Sum of current monthly charge amounts for customers in context | Customer | `SUM(monthly_charges)` | All customers in current context | `monthly_charges` is validated non-null | Currency, 2 decimals | Must match pandas sum; do not label as realized revenue without business confirmation |
| Average Monthly Charges | Mean current monthly charge per customer in context | Customer | `AVG(monthly_charges)` | Customers with a monthly-charge value; currently all customers | `monthly_charges` is validated non-null | Currency, 2 decimals | Must match pandas mean |
| Missing Total Charges | Customers whose source total charge was blank | Customer | Count where `total_charges IS NULL` | Customers in current context | Missingness is the metric | Whole number | Must match Phase 2 validation summary |

## Segment KPI rule

Every segmented churn rate must be shown with `total_customers` and `churned_customers`. A high rate from a small segment is not treated as equally stable or operationally important as a similar rate from a large segment.

## Eligibility rule

All processed customers are eligible because Phase 2 proved a complete, binary `churn` outcome and a complete unique customer key. If a future refresh introduces an invalid or missing outcome, the pipeline must fail rather than silently alter the denominator.
