WITH overall AS (
    SELECT * FROM vw_overall_kpis
),
segment_reconciliation AS (
    SELECT
        dimension,
        SUM(total_customers) AS segment_customers,
        SUM(churned_customers) AS segment_churned
    FROM vw_segment_kpis
    GROUP BY dimension
),
checks AS (
    SELECT
        'customer_id_unique' AS check_name,
        CASE WHEN COUNT(*) = COUNT(DISTINCT customer_id) THEN 'PASS' ELSE 'FAIL' END AS status,
        CAST(COUNT(DISTINCT customer_id) AS TEXT) AS actual,
        CAST(COUNT(*) AS TEXT) AS expected
    FROM vw_customer_clean

    UNION ALL

    SELECT
        'churned_plus_retained_equals_total',
        CASE WHEN churned_customers + retained_customers = total_customers THEN 'PASS' ELSE 'FAIL' END,
        CAST(churned_customers + retained_customers AS TEXT),
        CAST(total_customers AS TEXT)
    FROM overall

    UNION ALL

    SELECT
        'segment_customers_reconcile_' || dimension,
        CASE WHEN segment_customers = (SELECT total_customers FROM overall) THEN 'PASS' ELSE 'FAIL' END,
        CAST(segment_customers AS TEXT),
        CAST((SELECT total_customers FROM overall) AS TEXT)
    FROM segment_reconciliation

    UNION ALL

    SELECT
        'segment_churned_reconcile_' || dimension,
        CASE WHEN segment_churned = (SELECT churned_customers FROM overall) THEN 'PASS' ELSE 'FAIL' END,
        CAST(segment_churned AS TEXT),
        CAST((SELECT churned_customers FROM overall) AS TEXT)
    FROM segment_reconciliation
)
SELECT check_name, status, actual, expected
FROM checks
ORDER BY check_name;
