# Data provenance and handling

## Supplied source

| Field | Recorded value |
|---|---|
| Local filename | `Telco-Customer-Churn.csv` |
| Canonical local path | `data/raw/Telco-Customer-Churn.csv` |
| Date received | 2026-10-18 (Asia/Dhaka) |
| SHA-256 | `88BE4B93FBE0CC83421AF1C503794C97C342ECA914C1576DB7C276E61D61358A` |
| Observed header width | 21 columns |
| Dataset variant | Classic single-CSV candidate; confirm during Phase 2 |
| Source URL | Not supplied; confirm before portfolio publication |
| License/terms | To be confirmed from the original download source |

## Handling rules

- Files in `data/raw/` are immutable inputs.
- Raw and processed customer data are ignored by Git by default.
- Cleaning code must write generated outputs to `data/processed/`.
- A transformation must never overwrite its input.
- Every processing run must record row counts and validation results.
- Blank, zero, `No`, and service-not-applicable values remain distinct unless a documented business rule justifies a change.

The CSV originally supplied at the repository root was copied byte-for-byte into `data/raw/`; matching SHA-256 hashes verified the copy. The original was not modified or removed.
