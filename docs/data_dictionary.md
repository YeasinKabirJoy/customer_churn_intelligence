# Data dictionary

The processed table preserves the source meaning while using consistent `snake_case` names. Category values are not collapsed unless explicitly stated.

| Processed field | Type | Meaning / rule |
|---|---|---|
| `customer_id` | text | Candidate customer key; validated as complete and unique in Phase 2 |
| `gender` | text | Source-recorded gender category |
| `senior_citizen` | integer | Source binary coding: `0` or `1` |
| `partner` | text | Whether the customer has a partner |
| `dependents` | text | Whether the customer has dependents |
| `tenure` | integer | Customer tenure in months, validated from 0 through 72 |
| `phone_service` | text | Whether phone service is present |
| `multiple_lines` | text | `Yes`, `No`, or `No phone service` |
| `internet_service` | text | `DSL`, `Fiber optic`, or `No` |
| `online_security` | text | `Yes`, `No`, or `No internet service` |
| `online_backup` | text | `Yes`, `No`, or `No internet service` |
| `device_protection` | text | `Yes`, `No`, or `No internet service` |
| `tech_support` | text | `Yes`, `No`, or `No internet service` |
| `streaming_tv` | text | `Yes`, `No`, or `No internet service` |
| `streaming_movies` | text | `Yes`, `No`, or `No internet service` |
| `contract` | text | `Month-to-month`, `One year`, or `Two year` |
| `paperless_billing` | text | Whether paperless billing is enabled |
| `payment_method` | text | Source payment-method category |
| `monthly_charges` | decimal | Current monthly charge; nonnegative in the supplied file |
| `total_charges` | decimal, nullable | Cumulative charges; source blanks remain missing rather than becoming zero |
| `churn` | text | Source outcome: `Yes` or `No` |
| `senior_citizen_label` | text | Human-readable mapping of `senior_citizen`: `Yes` or `No` |
| `churn_flag` | integer | Analytical mapping: `Yes = 1`, `No = 0` |
| `total_charges_missing` | boolean | Indicates that the source `TotalCharges` value was blank |
| `tenure_band` | ordered text | `0-12`, `13-24`, `25-48`, `49-60`, or `61-72 months` |

`No`, `No internet service`, and `No phone service` are intentionally distinct. The latter two express that a service is not applicable because its prerequisite service is absent.
