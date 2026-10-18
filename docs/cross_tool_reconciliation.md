# Cross-tool reconciliation

| KPI | SQLite | Python | Power BI contract | Tableau contract |
|---|---:|---:|---:|---:|
| Total customers | 7,043 | 7,043 | 7,043 | 7,043 |
| Churned customers | 1,869 | 1,869 | 1,869 | 1,869 |
| Retained customers | 5,174 | 5,174 | 5,174 | 5,174 |
| Churn rate | 26.537% | 26.537% | 26.537% | 26.537% |
| Total monthly charges | $456,116.60 | $456,116.60 | $456,116.60 | $456,116.60 |
| Average monthly charges | $64.76 | $64.76 | $64.76 | $64.76 |
| Missing total charges | 11 | 11 | 11 | 11 |

SQLite and Python were executed and reconciled programmatically through 107 overall and segment comparisons. Power BI and Tableau values are frozen targets in measures, calculated fields, validation designs, and asset tests. Application validation remains pending until native `.pbix` and `.twbx` files are opened and interaction-tested.

ML metrics use the 1,409-customer test set and must never be reconciled to the 7,043-customer descriptive population. Evaluation tables remain disconnected from the descriptive model.

