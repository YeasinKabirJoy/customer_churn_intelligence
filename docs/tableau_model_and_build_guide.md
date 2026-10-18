# Tableau model and build guide

## 1. Connect the verified source

Open Tableau Desktop or Tableau Public, choose **Text file**, and select:

`data/processed/telco_customer_churn_clean.csv`

Confirm one logical table and these types: `customer_id` string, `senior_citizen` and `churn_flag` whole number, `tenure` whole number, `monthly_charges` and `total_charges` decimal number. Do not join the summary CSV files to the customer table: they have different grains and would duplicate customers.

## 2. Create governed measures

Open `reports/tableau/calculated_fields.txt`. In the Data pane, choose **Create calculated field** and create every field using the exact name and expression. Format `Churn Rate` and `Reference Churn Rate Difference` as percentages; charges as currency; counts as whole numbers.

## 3. Build the worksheets

### KPI sheets

Create one Text worksheet per KPI. Put the corresponding calculated field on Text. Keep every KPI filter-aware.

### Segment Risk and Volume

Use `Total Customers` on Columns and `Churn Rate` on Rows. Put the selected category on Detail and Label, `Churned Customers` on Size, and `Churn Rate Color` on Color. Start with `contract`; duplicate for `internet_service`, `payment_method`, or `tenure_band` when needed.

### Selected Segment Detail

Place the selected category on Rows and `Churn Rate` on Columns. Sort descending. Add `Total Customers`, `Churned Customers`, and `Average Monthly Charges` to Tooltip.

### Tenure Distribution

Create tenure bins of five months. Put the bin on Columns, customer count on Rows, and `Customer Status` on Color. This view explains lifecycle concentration without converting tenure to a causal claim.

## 4. Assemble and interact

Build the two dashboards exactly as specified in `reports/tableau/dashboard_specification.md`. Add a filter action from both segment views to the tenure distribution. Test mark selection and clearing. Filters must apply to all customer-source sheets.

## 5. Validate before saving

Clear all filters and confirm: 7,043 customers; 1,869 churned; 5,174 retained; 26.537% churn; $456,116.60 total monthly charges; $64.76 average monthly charges; 11 missing total charges. Confirm all three reference differences equal zero.

Then save as `reports/tableau/Telecom_Customer_Churn_Intelligence.twbx`. This is the only step requiring Tableau itself; do not treat the preview PNGs as a workbook.

