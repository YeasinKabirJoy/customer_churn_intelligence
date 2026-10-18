# Telecom Customer Churn Intelligence

A reproducible descriptive and diagnostic analytics project for understanding customer churn patterns in the IBM Telco Customer Churn sample.

## Business objective

Help a telecom retention or customer-success team understand where churn is concentrated, which observable customer and account characteristics are associated with churn, and which meaningful segments deserve investigation or a controlled retention experiment.

This project does not claim that observed characteristics cause churn. Predictive modeling, production deployment, and automated retention actions are outside the core scope.

## Audience

- Retention or customer-success manager
- Commercial or marketing analyst
- Analytics hiring manager reviewing the portfolio project

## Data contract (provisional until Phase 2 validation)

- Expected grain: one row per customer
- Candidate primary key: `customerID`
- Outcome: `Churn`, indicating whether the customer left
- Churn rate: distinct churned customers divided by distinct eligible customers in the current filter context
- Source of truth: the actual supplied CSV, not an assumed schema

These statements remain provisional until the Phase 2 audit proves the grain, key, categories, and missing-value behavior.

## Evidence rule

No count, rate, ranking, segment finding, revenue amount, or business-impact claim is reported until it is calculated from the supplied data and independently reconciled. Dashboard examples use placeholders until validation is complete.

## Repository map

```text
data/
  raw/          Immutable local source files (not committed)
  processed/    Generated analysis-ready outputs (not committed)
notebooks/      Numbered, question-first exploration notebooks
src/            Reusable Python cleaning and validation code
sql/            SQLite schema, views, KPI queries, and checks
reports/
  powerbi/      Power BI report, screenshots, and exports
  tableau/      Tableau workbook, screenshots, and exports
docs/           Charter, dictionaries, logs, QA, and narrative
tests/          Data assertions and reproducibility checks
```

## Current phase

Phase 7 lightweight ML complete - reproducible logistic-regression and shallow-tree pipelines, held-out evaluation, business-capacity metrics, risk deciles, fairness diagnostics, dashboard-ready predictions, and interview documentation are included. The ML layer is explicitly a proof of concept, not a production churn system.

## Setup

Create and activate a virtual environment, then install the project dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Validate the Phase 1 project foundation:

```powershell
python src/project_check.py
```

The check verifies required folders, the canonical raw file, its recorded hash, and local Python/SQLite availability. It does not calculate churn findings.

Run the repeatable Phase 2 cleaning and validation pipeline:

```powershell
python src/data_pipeline.py
python -m pytest
```

Build and validate the SQLite analytical layer:

```powershell
python src/sql_pipeline.py
python -m pytest
```

Generate the Python EDA outputs and charts:

```powershell
python src/eda_pipeline.py
python -m pytest
```

Generate the Tableau dashboard previews:

```powershell
python src/tableau_preview.py
python -m pytest
```

Train and evaluate the Phase 7 proof-of-concept models:

```powershell
python src/ml_pipeline.py
python -m pytest
```

## Planned workflow

1. Frame the project and record provenance.
2. Audit and clean the supplied dataset.
3. Build and reconcile the SQLite analytical layer.
4. Perform Python EDA using governed KPI definitions.
5. Build and validate Power BI and Tableau reports.
6. Reconcile all tools and prepare the executive narrative.
7. Package the portfolio and interview walkthrough.

Each phase stops at a learning and validation gate before the next phase begins.
