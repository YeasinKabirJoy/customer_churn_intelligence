-- Governed overall KPI reference.
-- Customer denominator: distinct customers in the current filter context.
SELECT
    total_customers,
    churned_customers,
    retained_customers,
    ROUND(churn_rate, 6) AS churn_rate,
    ROUND(total_monthly_charges, 2) AS total_monthly_charges,
    ROUND(average_monthly_charges, 2) AS average_monthly_charges,
    missing_total_charges
FROM vw_overall_kpis;
