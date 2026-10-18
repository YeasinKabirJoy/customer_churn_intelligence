-- All governed segmentation results. Each rate is paired with customer volume.
SELECT
    dimension,
    segment,
    total_customers,
    churned_customers,
    retained_customers,
    ROUND(churn_rate, 6) AS churn_rate,
    churn_rate_rank,
    volume_rank,
    ROUND(share_of_dimension_churned_customers, 6) AS share_of_dimension_churned_customers
FROM vw_segment_rankings
ORDER BY dimension, churn_rate_rank, segment;
