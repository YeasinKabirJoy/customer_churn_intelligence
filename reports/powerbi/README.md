# Power BI deliverables

- `theme.json`: governed report palette
- `ml_measures.dax`: held-out evaluation measures for the predictive page
- `ml_dashboard_specification.md`: predictive-page data and layout contract
- `predictive_demonstration_preview.png`: target ML-page layout
- `measures.dax`: authoritative measure definitions
- `power_query.m`: typed connection to the processed customer table
- `model.tmdl`: one-step semantic-model script for Power BI Desktop's TMDL view
- `.pbix`: interactive report created in Power BI Desktop
- Screenshots/PDF exports: portable review fallback

The build and model rationale are documented in `docs/powerbi_model_and_build_guide.md`. Metrics must reconcile with `data/processed/kpi_reference.csv` and `segment_kpis.csv`.
