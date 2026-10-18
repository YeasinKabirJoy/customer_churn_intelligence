# Power BI learning guide and model answers

## Power Query versus DAX

Power Query runs during data preparation and refresh. It connects to the processed CSV and assigns data types. DAX evaluates measures after the model is loaded and responds to report filters and visual context.

Cleaning remains in Python so Power BI does not silently become a second, inconsistent cleaning pipeline.

## Calculated column versus measure

A calculated column stores one value for every row during refresh. A measure calculates a result when a visual queries it. Total Customers and Churn Rate are measures because their values must change under slicers.

`churn_flag` is a row-level column. `Churned Customers` is a filter-responsive measure.

## Row context versus filter context

Row context identifies the current row, commonly in calculated columns and iterator functions. Filter context is the subset of model rows selected by slicers, page filters, visual categories, and DAX filters.

The churn measures rely on filter context. A contract slicer restricts the rows first; `CALCULATE` then adds `churn_flag = 1` for the numerator.

## Token-by-token measure explanation

```DAX
Churn Rate = DIVIDE ( [Churned Customers], [Total Customers] )
```

- `Churn Rate`: reusable measure name
- `DIVIDE`: safe division function
- `[Churned Customers]`: numerator evaluated in current filter context
- `[Total Customers]`: denominator evaluated in the same context
- Blank result: returned if the denominator is zero

## Why cards change under slicers

Measures are recalculated for the active filter context. Selecting Fiber optic restricts the table to fiber customers, so Total Customers, Churned Customers, and Churn Rate all answer the fiber-specific question.

## Three validation methods

1. Compare unfiltered cards to `kpi_reference.csv`.
2. Compare segment bars and tooltips to `segment_kpis.csv`.
3. Use the validation-difference measures; each must equal zero when all filters are cleared.

## Common mismatch causes

- Counting rows rather than distinct customers
- Averaging displayed churn rates
- A slicer or visual interaction remaining active
- Different null handling
- Using a calculated column instead of a measure
- Stale data because the report was not refreshed
- Display rounding mistaken for a calculation mismatch
