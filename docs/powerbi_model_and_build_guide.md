# Power BI model and build guide

## Model decision

The processed dataset has one row per unique customer and no separate transactional or multi-entity tables. The implemented Power BI model therefore uses one governed customer table named `telco_customer_churn_clean`.

A larger production model would use a customer fact/snapshot table with conformed dimensions for contract, service, payment method, tenure band, and date. Creating nine one-column dimensions for this small static sample would add relationships without improving correctness or reuse. The flat-table choice is documented rather than accidental.

```text
Future star schema

DimContract ---------+
DimInternetService --+
DimPaymentMethod ----+--> FactCustomerSnapshot <-- DimCustomerProfile
DimTenureBand -------+             |
DimDate -------------+             +-- governed additive and distinct-customer measures
```

## Data source

- Source: `data/processed/telco_customer_churn_clean.csv`
- Grain: one row per customer
- Key: `customer_id`
- Rows expected with no filters: 7,043
- Refresh dependency: run `python src/data_pipeline.py` first

The report consumes the processed table rather than repeating business cleaning in Power Query. Power Query sets explicit types and exposes source/refresh errors.

## Column types

- Text/dimensions: identifiers, profile categories, service categories, contract, payment method, churn, tenure band
- Whole numbers: `senior_citizen`, `tenure`, `churn_flag`
- Decimal/currency: `monthly_charges`, `total_charges`
- Boolean: `total_charges_missing`

Do not summarize `customer_id`, category codes, or `churn_flag` directly in visuals. Use measures.

## Measures

The authoritative DAX is stored in `reports/powerbi/measures.dax`.

Conceptual pattern:

```DAX
Total Customers =
DISTINCTCOUNT ( 'telco_customer_churn_clean'[customer_id] )

Churned Customers =
CALCULATE (
    [Total Customers],
    'telco_customer_churn_clean'[churn_flag] = 1
)

Churn Rate =
DIVIDE ( [Churned Customers], [Total Customers] )
```

`DISTINCTCOUNT` preserves customer grain. `CALCULATE` modifies the current filter context to churned customers. `DIVIDE` safely returns blank if no customers remain in context.

## Page 1 - Executive Overview

Purpose: show the size of the churn problem and the largest verified concentrations.

Recommended 16:9 layout:

1. Title and short definition line
2. Four KPI cards: Total Customers, Churned Customers, Churn Rate, Average Monthly Charges
3. Churn rate by contract with customer count available in tooltip
4. Churn rate by tenure band with customer count available in tooltip
5. Churn rate by internet service
6. Decision note: investigate early-tenure month-to-month and fiber experience; association is not causation
7. Slicers: Contract, Internet Service, Tenure Band, Payment Method, Senior Citizen

Top-left priority belongs to contract and tenure because both rate and affected volume are substantial.

## Page 2 - Segment Explorer

Purpose: let an analyst compare volume, rate, charges, and customer details under shared filters.

- Clustered bar: Total Customers and Churned Customers by selected segment
- Bar chart: Churn Rate by selected dimension
- Box/distribution substitute using binned tenure or charge ranges if native visuals are required
- Detail table: segment, Total Customers, Churned Customers, Churn Rate, Average Monthly Charges
- Same five slicers as the executive page
- Cross-highlight interactions enabled only when they preserve an understandable denominator

## Page 3 - Validation

Purpose: make reconciliation visible to the builder without presenting it as an executive page.

Cards with all filters cleared:

| Measure | Expected |
|---|---:|
| Total Customers | 7,043 |
| Churned Customers | 1,869 |
| Retained Customers | 5,174 |
| Churn Rate | 26.537% |
| Total Monthly Charges | 456,116.60 |
| Average Monthly Charges | 64.76 |
| Missing Total Charges | 11 |

All four `Validation ... Difference` measures must show zero with filters cleared.

## Formatting and accessibility

- Primary navy: `#17324D`
- Retained/neutral teal: `#138A8A`
- Churn/highlight orange: `#E28A2B`
- Supporting light blue: `#7DB7D8`
- White background with high-contrast text
- Minimum body text target: 11 pt at final display size
- Never use color as the only indicator; retain labels and titles
- Set alt text for every meaningful visual
- Use question-led titles and state the denominator in tooltips
- Format churn rate as percentage with one decimal for presentation; retain full precision in validation

## Interaction tests

1. Clear all slicers and reconcile every KPI.
2. Select each slicer independently and verify both numerator and denominator change.
3. Confirm that selecting a chart does not unexpectedly filter KPI cards when highlight-only behavior is intended.
4. Confirm blank total charges remain blank and are excluded from averages by DAX default behavior.
5. Reset filters and verify all validation differences return to zero.
