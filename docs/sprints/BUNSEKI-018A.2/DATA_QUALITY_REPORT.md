# Academic data quality

Profiles: 170. `academic_period` does not exist.

| Field | Null | Empty | Exact variants | Lower/trim variants |
|---|---:|---:|---:|---:|
| subject | 116 | 0 | 4 | 4 |
| course | 39 | 6 | 56 | 55 |
| course_level | 116 | 0 | 5 | 5 |
| parallel | 116 | 0 | 1 | 1 |
| cohort | 116 | 0 | 5 | 5 |
| teacher | 81 | 11 | 43 | 32 |

The populated subject values are four controlled-looking labels, but 116 profiles have no subject. Parallel is only `4-A1` where populated. Cohort has one research code (42) plus four course-like text labels. Course is severely overloaded (55 normalized variants, including semester, subject, shift and program-like forms), so it must not be parsed automatically into relational IDs. Teacher has 43 exact / 32 normalized values; identities are intentionally not reported.

Historical classification: `SAFE_TO_MIGRATE=0`; `INCOMPLETE=161` (one or more subject/parallel/cohort/teacher absent); `NEEDS_MANUAL_REVIEW=9` (those fields populated but academic period absent); `AMBIGUOUS=0` under the strict rule that no inference is made. Every record lacks the required period, so none can reconstruct the full enrollment tuple automatically.
