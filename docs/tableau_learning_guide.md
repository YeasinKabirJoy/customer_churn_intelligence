# Tableau learning and interview guide

## What you must understand

**Dimension vs measure:** a dimension slices or identifies marks, such as contract or payment method. A measure is aggregated, such as customer count or churn rate.

**Discrete vs continuous:** discrete fields create headers and categories; continuous fields create axes. The same numeric field can be used either way depending on the analytical question.

**Aggregation and view grain:** Tableau computes a measure at the level of detail created by dimensions in the view. Adding `contract` changes one overall churn rate into one rate per contract category.

**Filter context:** the numerator and denominator of churn rate must be calculated inside the same active filters. `COUNTD` protects the customer metric if duplicate rows ever appear, but duplicates should still be investigated.

**Table calculation vs calculated field:** a normal calculated field operates on source rows or aggregated values. A table calculation works on the marks already returned to the view, so it can change when layout or addressing changes.

**LOD expression:** a level-of-detail expression fixes or changes the dimensional scope of a calculation. It is useful for stable benchmarks, but unnecessary for the main filter-aware churn rate here.

**Dashboard action:** an action connects views. Selecting a segment filters the tenure distribution, enabling guided exploration without adding many separate dashboards.

## Answers to memorize

**Why Tableau after Power BI?** Tableau is used for focused visual exploration and coordinated views, while the same governed KPI definitions prove that tool choice does not change the business result.

**Why use COUNTD(customer_id)?** The business entity is a customer. Distinct counting aligns the KPI with that entity and makes the intended grain explicit.

**Why show volume beside churn rate?** A high rate in a tiny segment and a slightly lower rate in a large segment imply different retention priorities. Rate supplies risk; volume supplies scale.

**Why not call association causation?** The dataset is observational. Contract, tenure, or service categories may correlate with churn, but no controlled intervention or causal design isolates their effect.

**Why keep missing Total Charges?** Missing does not prove zero. Retaining the 11 values preserves source meaning and customer counts while making missingness visible.

**How did you validate Tableau?** I cleared filters, reconciled seven KPI outputs to SQLite and Python references, checked three zero-difference measures, tested dashboard actions, and verified that filters affect numerator and denominator consistently. The current source package is ready for that Desktop validation; a workbook must not be claimed until opened and tested in Tableau.

