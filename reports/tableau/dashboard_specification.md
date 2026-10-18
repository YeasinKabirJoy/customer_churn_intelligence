# Tableau dashboard specification

## Dashboard 1 — Churn Segment Explorer

Canvas: fixed 1,440 × 900. Use a focused two-view analysis rather than copying every Power BI visual.

1. Header: title, short subtitle, and five KPI tiles.
2. Left view — `Segment Risk and Volume`: scatter plot with `Total Customers` on Columns, `Churn Rate` on Rows, `segment` on Detail/Label, and `Churned Customers` on Size. Color by `Churn Rate Color`.
3. Right view — `Selected Segment Detail`: horizontal bars for churn rate, sorted descending, with customer count in the label.
4. Bottom view — `Tenure Distribution`: histogram of tenure, colored by `Customer Status`.
5. Filters: contract, internet_service, tenure_band, payment_method, senior_citizen_label. Apply to all worksheets using the customer source.
6. Dashboard action: selecting a mark in either segment view filters the tenure distribution. Clearing the selection restores all customers.

Tooltips must show segment, total customers, churned customers, churn rate, and average monthly charges. Always show population with rate.

## Dashboard 2 — Validation

Show the seven governed KPI values and the three reference-difference fields. With all filters cleared, all differences must be zero. Include the data-source refresh timestamp and a note that 11 missing `total_charges` values are intentionally retained.

## Formatting

- Navy `#17324D`: titles and primary text
- Teal `#138A8A`: normal analytical marks
- Orange `#E28A2B`: churn/high-risk emphasis
- Green `#278A5B`: validation pass
- Pale background `#EDF4F7`
- Use color plus text/position; never encode meaning by color alone.

