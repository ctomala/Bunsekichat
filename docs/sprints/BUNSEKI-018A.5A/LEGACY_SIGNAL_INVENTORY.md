# Legacy academic signal inventory

Source: certified pre-018A.4B.1 backup restored locally in PostgreSQL 17. This is aggregate-only evidence; no individual value, username, name, email, identifier, or location was inspected or recorded.

`USERS_TOTAL=171`; `PROFILES_TOTAL=170`; role distribution: 170 student, 1 admin, 0 teacher.

| Legacy field | Populated | Missing | Distinct normalized values |
|---|---:|---:|---:|
| teacher | 78 | 92 | 32 |
| subject | 54 | 116 | 4 |
| course | 125 | 45 | 55 |
| parallel | 54 | 116 | 1 |
| cohort | 54 | 116 | 5 |
| course_level | 54 | 116 | 5 |
| level | 170 | 0 | 4 |
| research_group | 170 | 0 | 2 |

There is no legacy academic-period field. Under a deliberately strict definition (one or more of teacher, subject, course, parallel, or cohort absent), 161 profiles have major academic incompleteness. These free-text signals are evidence for manual review only, never evidence for automatic enrollment, teacher assignment, period assignment, or cohort inference.
