# Reproducibility runbook

Place the source CSV at the repository root as `Telco-Customer-Churn.csv`; it is intentionally excluded from Git.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python src/project_check.py
python src/data_pipeline.py
python src/sql_pipeline.py
python src/eda_pipeline.py
python src/powerbi_preview.py
python src/tableau_preview.py
python src/ml_pipeline.py
python src/ml_dashboard_preview.py
python -m pytest -q
```

Generated customer-level data and databases remain local under `data/processed/`. Governed summaries, figures, source contracts, and model artifacts are stored under `reports/`. Use the BI build guides to create, validate, and save ignored `.pbix` and `.twbx` files locally.

