# SQLite analytical layer

The analytical layer is rebuilt with:

```powershell
python src/sql_pipeline.py
```

Files execute in numeric order:

- `01_schema.sql`: typed customer table, constraints, and indexes
- `02_views.sql`: governed customer, KPI, segment, charge, and ranking views
- `03_kpis.sql`: overall KPI reference query
- `04_segments.sql`: segmentation and ranking query
- `05_charge_summary.sql`: charge summary with explicit missing-value counts
- `06_sanity_checks.sql`: customer and segment reconciliation checks

Generated SQLite and CSV outputs live in `data/processed/` and are local-only by default.
