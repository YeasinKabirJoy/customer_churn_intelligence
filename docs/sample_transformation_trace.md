# Sample transformation trace

These three records demonstrate the cleaning rules without using them as business findings.

## 1. Standard numeric and label conversion

Customer `7590-VHVEG`:

- `customerID` becomes `customer_id`; its value is unchanged.
- Text values are trimmed but retain their original meanings.
- `SeniorCitizen = "0"` becomes integer `senior_citizen = 0` and label `senior_citizen_label = "No"`.
- `tenure = "1"` becomes integer `1` and maps to `tenure_band = "0-12 months"`.
- `MonthlyCharges = "29.85"` and `TotalCharges = "29.85"` become numeric values.
- `Churn = "No"` remains the source category and produces `churn_flag = 0`.

## 2. Preserving a meaningful not-applicable category

Customer `7469-LKBCI` has `InternetService = "No"`. Related fields contain `"No internet service"`.

The pipeline preserves that phrase instead of converting it to ordinary `"No"` because the meanings differ:

- `No` means the customer has internet service but did not select that add-on.
- `No internet service` means the add-on is not applicable because the prerequisite service is absent.

The customer's tenure of 16 months maps to `13-24 months`.

## 3. Preserving missing charge information

Customer `4472-LVYGI` has a blank source `TotalCharges` value and tenure of zero months.

- The blank becomes an explicit missing numeric value.
- `total_charges_missing` becomes `True`.
- No zero is invented.
- The customer remains in the processed dataset.
- Tenure maps to `0-12 months`.

All 11 blank `TotalCharges` records have zero tenure, but that pattern alone does not prove the intended monetary value. Preserving the null keeps the uncertainty visible and lets each later calculation state its null-handling rule.
