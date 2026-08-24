# Academic code normalization

`subjects.code` is stable and uniquely identifies the catalog subject. `ALG` is technically and semantically compatible with the Founder naming decision. `ALG_DISPLAY_NAME_CHANGE_REQUIRED=YES`: update only `subjects.name` from the current `Álgebra` to `Álgebra Lineal` in the authorized 5B.1 transaction; do not introduce a new subject code.

`academic_periods.status` admits only lowercase `draft`, `active`, or `closed`; the prepared manifest uses `draft`. `ACTIVE`, `OPEN`, and `CURRENT` are not schema values. The period name and exact dates require Founder confirmation.

The Founder approved the following split. Course codes identify the period offering; parallel codes identify the operational section within that course:

| Subject | Source academic code | Proposed course code | Proposed parallel code | Proposed cohort code | Confidence | Founder confirmation |
|---|---|---|---|---|---|---|
| CALC-DIF | PMF-MA-4-A1 | PMF-MA-4 | A1 | 2026-2027-CII-CALC-DIF-PMF-MA-4-A1 | confirmed | no |
| CALC-DIF | PMF-MA-4-A2 | PMF-MA-4 | A2 | 2026-2027-CII-CALC-DIF-PMF-MA-4-A2 | confirmed | no |
| EST | PMF-MA-3-3A1 | PMF-MA-3 | 3A1 | 2026-2027-CII-EST-PMF-MA-3-3A1 | confirmed | no |
| EST | PMF-MA-3-3A2 | PMF-MA-3 | 3A2 | 2026-2027-CII-EST-PMF-MA-3-3A2 | confirmed | no |
| ALG | PMF-MA-5-5A1 | PMF-MA-5 | 5A1 | 2026-2027-CII-ALG-PMF-MA-5-5A1 | confirmed | no |
| ALG-ELEM | PMF-MA-2-2A1 | PMF-MA-2 | 2A1 | 2026-2027-CII-ALG-ELEM-PMF-MA-2-2A1 | confirmed | no |
| CALC-INT | PMF-MA-5C-5C1 | PMF-MA-5C | 5C1 | 2026-2027-CII-CALC-INT-PMF-MA-5C-5C1 | confirmed | no |
| CALC-INT | PMF-MA-5C-5C2 | PMF-MA-5C | 5C2 | 2026-2027-CII-CALC-INT-PMF-MA-5C-5C2 | confirmed | no |

The exact cohort convention is `{period}-{subject}-{course}-{parallel}`. It is non-PII, stable, and one per initial parallel. It does not make cohort equivalent to parallel. `EXPECTED_COHORTS=8`.
