CREATE VIEW vw_customer_clean AS
SELECT *
FROM customer_churn;

CREATE VIEW vw_overall_kpis AS
SELECT
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN churn_flag = 1 THEN customer_id END) AS churned_customers,
    COUNT(DISTINCT CASE WHEN churn_flag = 0 THEN customer_id END) AS retained_customers,
    1.0 * COUNT(DISTINCT CASE WHEN churn_flag = 1 THEN customer_id END)
        / NULLIF(COUNT(DISTINCT customer_id), 0) AS churn_rate,
    SUM(monthly_charges) AS total_monthly_charges,
    AVG(monthly_charges) AS average_monthly_charges,
    SUM(CASE WHEN total_charges IS NULL THEN 1 ELSE 0 END) AS missing_total_charges
FROM vw_customer_clean;

CREATE VIEW vw_segment_kpis AS
WITH segment_base AS (
    SELECT 'contract' AS dimension, contract AS segment, customer_id, churn_flag FROM vw_customer_clean
    UNION ALL
    SELECT 'tenure_band', tenure_band, customer_id, churn_flag FROM vw_customer_clean
    UNION ALL
    SELECT 'internet_service', internet_service, customer_id, churn_flag FROM vw_customer_clean
    UNION ALL
    SELECT 'payment_method', payment_method, customer_id, churn_flag FROM vw_customer_clean
    UNION ALL
    SELECT 'paperless_billing', paperless_billing, customer_id, churn_flag FROM vw_customer_clean
    UNION ALL
    SELECT 'senior_citizen', senior_citizen_label, customer_id, churn_flag FROM vw_customer_clean
    UNION ALL
    SELECT 'gender', gender, customer_id, churn_flag FROM vw_customer_clean
    UNION ALL
    SELECT 'partner', partner, customer_id, churn_flag FROM vw_customer_clean
    UNION ALL
    SELECT 'dependents', dependents, customer_id, churn_flag FROM vw_customer_clean
)
SELECT
    dimension,
    segment,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN churn_flag = 1 THEN customer_id END) AS churned_customers,
    COUNT(DISTINCT CASE WHEN churn_flag = 0 THEN customer_id END) AS retained_customers,
    1.0 * COUNT(DISTINCT CASE WHEN churn_flag = 1 THEN customer_id END)
        / NULLIF(COUNT(DISTINCT customer_id), 0) AS churn_rate
FROM segment_base
GROUP BY dimension, segment;

CREATE VIEW vw_charge_summary_by_churn AS
SELECT
    churn,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(total_charges) AS customers_with_total_charges,
    SUM(CASE WHEN total_charges IS NULL THEN 1 ELSE 0 END) AS missing_total_charges,
    AVG(monthly_charges) AS average_monthly_charges,
    MIN(monthly_charges) AS minimum_monthly_charges,
    MAX(monthly_charges) AS maximum_monthly_charges,
    AVG(total_charges) AS average_total_charges,
    MIN(total_charges) AS minimum_total_charges,
    MAX(total_charges) AS maximum_total_charges
FROM vw_customer_clean
GROUP BY churn;

CREATE VIEW vw_segment_rankings AS
SELECT
    dimension,
    segment,
    total_customers,
    churned_customers,
    retained_customers,
    churn_rate,
    DENSE_RANK() OVER (
        PARTITION BY dimension
        ORDER BY churn_rate DESC
    ) AS churn_rate_rank,
    DENSE_RANK() OVER (
        PARTITION BY dimension
        ORDER BY total_customers DESC
    ) AS volume_rank,
    1.0 * churned_customers
        / NULLIF(SUM(churned_customers) OVER (PARTITION BY dimension), 0)
        AS share_of_dimension_churned_customers
FROM vw_segment_kpis;
