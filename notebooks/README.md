# Python analysis

The reproducible EDA is implemented in `src/eda_pipeline.py` rather than hiding transformations in notebook-only cells. It is organized around business questions and exports governed tables, findings, and figures.

Run:

```powershell
python src/eda_pipeline.py
```

An exploratory notebook may later call the same named functions, but the script remains the reproducible source of truth.
