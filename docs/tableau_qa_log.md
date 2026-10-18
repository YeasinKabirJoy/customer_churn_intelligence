# Tableau QA log

| Check | Expected | Status |
|---|---:|---|
| Source grain | One row per customer | Ready from validated CSV |
| Total customers | 7,043 | Reference frozen |
| Churned customers | 1,869 | Reference frozen |
| Retained customers | 5,174 | Reference frozen |
| Churn rate | 26.537% | Reference frozen |
| Total monthly charges | $456,116.60 | Reference frozen |
| Average monthly charges | $64.76 | Reference frozen |
| Missing total charges | 11 | Reference frozen |
| Static layout review | No clipping; readable hierarchy | Passed visual inspection |
| Native workbook open/save | Valid `.twb/.twbx` | Blocked: Windows control service unavailable |
| Filters/actions in Tableau | Expected coordinated behavior | Pending native workbook |

The final two interactive checks cannot be inferred from PNG previews. They must be completed in Tableau Desktop/Public before presenting an interactive workbook.

