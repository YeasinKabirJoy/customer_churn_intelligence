-- Charge summaries retain the missing-value denominator explicitly.
SELECT
    churn,
    total_customers,
    customers_with_total_charges,
    missing_total_charges,
    ROUND(average_monthly_charges, 2) AS average_monthly_charges,
    ROUND(minimum_monthly_charges, 2) AS minimum_monthly_charges,
    ROUND(maximum_monthly_charges, 2) AS maximum_monthly_charges,
    ROUND(average_total_charges, 2) AS average_total_charges,
    ROUND(minimum_total_charges, 2) AS minimum_total_charges,
    ROUND(maximum_total_charges, 2) AS maximum_total_charges
FROM vw_charge_summary_by_churn
ORDER BY churn;
