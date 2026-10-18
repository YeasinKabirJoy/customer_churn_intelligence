PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS vw_segment_rankings;
DROP VIEW IF EXISTS vw_charge_summary_by_churn;
DROP VIEW IF EXISTS vw_segment_kpis;
DROP VIEW IF EXISTS vw_overall_kpis;
DROP VIEW IF EXISTS vw_customer_clean;
DROP TABLE IF EXISTS customer_churn;

CREATE TABLE customer_churn (
    customer_id TEXT PRIMARY KEY NOT NULL,
    gender TEXT NOT NULL CHECK (gender IN ('Female', 'Male')),
    senior_citizen INTEGER NOT NULL CHECK (senior_citizen IN (0, 1)),
    partner TEXT NOT NULL CHECK (partner IN ('No', 'Yes')),
    dependents TEXT NOT NULL CHECK (dependents IN ('No', 'Yes')),
    tenure INTEGER NOT NULL CHECK (tenure BETWEEN 0 AND 72),
    phone_service TEXT NOT NULL CHECK (phone_service IN ('No', 'Yes')),
    multiple_lines TEXT NOT NULL CHECK (multiple_lines IN ('No', 'No phone service', 'Yes')),
    internet_service TEXT NOT NULL CHECK (internet_service IN ('DSL', 'Fiber optic', 'No')),
    online_security TEXT NOT NULL CHECK (online_security IN ('No', 'No internet service', 'Yes')),
    online_backup TEXT NOT NULL CHECK (online_backup IN ('No', 'No internet service', 'Yes')),
    device_protection TEXT NOT NULL CHECK (device_protection IN ('No', 'No internet service', 'Yes')),
    tech_support TEXT NOT NULL CHECK (tech_support IN ('No', 'No internet service', 'Yes')),
    streaming_tv TEXT NOT NULL CHECK (streaming_tv IN ('No', 'No internet service', 'Yes')),
    streaming_movies TEXT NOT NULL CHECK (streaming_movies IN ('No', 'No internet service', 'Yes')),
    contract TEXT NOT NULL CHECK (contract IN ('Month-to-month', 'One year', 'Two year')),
    paperless_billing TEXT NOT NULL CHECK (paperless_billing IN ('No', 'Yes')),
    payment_method TEXT NOT NULL CHECK (
        payment_method IN (
            'Bank transfer (automatic)',
            'Credit card (automatic)',
            'Electronic check',
            'Mailed check'
        )
    ),
    monthly_charges REAL NOT NULL CHECK (monthly_charges >= 0),
    total_charges REAL CHECK (total_charges IS NULL OR total_charges >= 0),
    churn TEXT NOT NULL CHECK (churn IN ('No', 'Yes')),
    senior_citizen_label TEXT NOT NULL CHECK (senior_citizen_label IN ('No', 'Yes')),
    churn_flag INTEGER NOT NULL CHECK (churn_flag IN (0, 1)),
    total_charges_missing INTEGER NOT NULL CHECK (total_charges_missing IN (0, 1)),
    tenure_band TEXT NOT NULL CHECK (
        tenure_band IN ('0-12 months', '13-24 months', '25-48 months', '49-60 months', '61-72 months')
    ),
    CHECK (
        (senior_citizen = 1 AND senior_citizen_label = 'Yes') OR
        (senior_citizen = 0 AND senior_citizen_label = 'No')
    ),
    CHECK (
        (churn = 'Yes' AND churn_flag = 1) OR
        (churn = 'No' AND churn_flag = 0)
    ),
    CHECK (
        (total_charges IS NULL AND total_charges_missing = 1) OR
        (total_charges IS NOT NULL AND total_charges_missing = 0)
    )
);

CREATE INDEX idx_customer_churn_contract ON customer_churn (contract);
CREATE INDEX idx_customer_churn_tenure_band ON customer_churn (tenure_band);
CREATE INDEX idx_customer_churn_internet_service ON customer_churn (internet_service);
CREATE INDEX idx_customer_churn_payment_method ON customer_churn (payment_method);
CREATE INDEX idx_customer_churn_churn_flag ON customer_churn (churn_flag);
