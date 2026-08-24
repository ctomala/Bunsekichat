# Course, parallel, and cohort policy

Course is the offering of exactly one `subjects` record in exactly one `academic_periods` record. Its code is unique within that period, so a recommended human convention is a stable subject/period-specific offering code, not a global assumption. The five existing subject codes are `ALG`, `ALG-ELEM`, `CALC-DIF`, `CALC-INT`, and `EST`; no new subject is needed for the first population absent a separate catalog decision.

Parallel is an operational class section: required `course_id`, `code`, and `name`; code is unique only within its course. Labels such as A, B, C or 4-A1 are permitted institutional choices, not enforced formats. Active status is represented by `active`.

Cohort is a persistent analytical grouping scoped to one course: required `course_id`, globally unique `code`, `name`, and `status`; optional `research_group`. It is not synonymous with Parallel. Use a non-PII cohort code and a research pseudonym/group only where approved. An enrollment must reference both a parallel and cohort belonging to the same course; the database enforces that invariant.

Because `cohorts.code` is global, choose codes that remain unique across periods and courses. Because cohort status is unconstrained text, 018A.5B must use a controlled approved vocabulary.
