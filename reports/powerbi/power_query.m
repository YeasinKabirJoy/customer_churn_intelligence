// Reference implementation for loading the governed Phase 2 output.
// Update only the Source path when the repository is moved.
let
    Source = Csv.Document(
        File.Contents("D:\others\Github\customer_churn_intelligence\data\processed\telco_customer_churn_clean.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"customer_id", type text},
            {"gender", type text},
            {"senior_citizen", Int64.Type},
            {"partner", type text},
            {"dependents", type text},
            {"tenure", Int64.Type},
            {"phone_service", type text},
            {"multiple_lines", type text},
            {"internet_service", type text},
            {"online_security", type text},
            {"online_backup", type text},
            {"device_protection", type text},
            {"tech_support", type text},
            {"streaming_tv", type text},
            {"streaming_movies", type text},
            {"contract", type text},
            {"paperless_billing", type text},
            {"payment_method", type text},
            {"monthly_charges", Currency.Type},
            {"total_charges", Currency.Type},
            {"churn", type text},
            {"senior_citizen_label", type text},
            {"churn_flag", Int64.Type},
            {"total_charges_missing", type logical},
            {"tenure_band", type text}
        }
    )
in
    TypedColumns
