# SQL learning guide and model answers

## Why use `COUNT(DISTINCT customer_id)`?

The current customer table has one row per customer, so `COUNT(*)` and the distinct count agree. The governed KPI still uses a distinct customer count because future joins can create multiple rows per customer. The KPI is defined at customer grain, not physical row grain.

## Why not average segment churn rates?

Segments have different customer counts. An unweighted average gives a small segment the same influence as a large segment. The correct overall rate is total churned customers divided by total eligible customers, which is equivalent to a customer-count-weighted segment rate when segments are mutually exclusive and complete.

## How filter context changes the denominator

Filtering to a contract type restricts both the churned-customer numerator and total-customer denominator to that contract. The result answers “what share of customers in this contract churned?” It does not divide that segment's churned customers by the entire company population.

## Why joins can corrupt counts

A one-to-many join repeats a customer's row once for every matching detail record. `COUNT(*)`, sums, and averages can then be inflated. Three required join checks are:

1. Compare row counts before and after the join.
2. Compare distinct customer counts before and after the join.
3. Count joined rows per customer and inspect keys with more than one match.

## Safe division

SQLite uses `numerator / NULLIF(denominator, 0)`. `NULLIF` converts a zero denominator to null, so the result becomes null rather than raising an error or presenting a misleading zero rate.

## Query evaluation pattern

For the segment query, think in this practical order:

1. Read customer rows from the governed view.
2. Assign a dimension name and segment value.
3. Group customers by dimension and segment.
4. Count distinct total, churned, and retained customers.
5. Divide churned by total within each group.
6. Apply window functions to rank rates and volumes without collapsing the grouped rows.

## CTE and window-function purpose

A CTE names an intermediate result so complicated logic can be read and tested in stages. A window function calculates across related result rows while keeping each row visible. Here, `DENSE_RANK` ranks segments within each dimension, and the windowed sum calculates each segment's share of churned customers.
