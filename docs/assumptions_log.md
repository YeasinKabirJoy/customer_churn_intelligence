# Assumptions log

Assumptions are temporary statements to test, not facts to silently embed in code.

| ID | Date | Assumption | Validation needed | Status |
|---|---|---|---|---|
| A-001 | 2026-10-18 | One CSV row represents one customer. | Compared row count, complete IDs, distinct IDs, and duplicate rows. | Confirmed for supplied file |
| A-002 | 2026-10-18 | `customerID` is the primary key. | Tested uniqueness, blanks, and missing values. | Confirmed for supplied file |
| A-003 | 2026-10-18 | `Churn` contains a binary customer outcome. | Inspected actual trimmed values and missingness. | Confirmed: `Yes`/`No` |
| A-004 | 2026-10-18 | The supplied file is the classic IBM single-CSV variant. | Compared actual 21-field schema with the expected classic structure. | Confirmed structurally; provenance URL open |
| A-005 | 2026-10-18 | A flat customer table is sufficient for the core analysis. | Confirmed one row per unique customer in the supplied file. | Confirmed for core analysis |
| A-006 | 2026-10-18 | SQLite supports all required core query patterns. | Run compatibility checks for CTEs, windows, safe division, and exports. | Open |
