# Academic period policy

An academic period is a named, coded lifecycle record. Required real fields are `code`, `name`, and `status`; `start_date` and `end_date` are nullable in the current schema but are required by the future population policy unless the Founder explicitly records why a date is unavailable.

Codes must be institutionally unique and stable. `2026-C1` and `2026-C2` are examples only, not proposed production values. Create a period initially as `draft`, validate all courses and assignments, then activate only by an explicitly authorized lifecycle operation. A closed period must receive no new enrollment without an explicit exception process.

The schema has no date-order or overlap constraint. 018A.5B preflight must reject end dates before start dates and flag overlapping active periods for Founder confirmation. `ACADEMIC_PERIOD_DECISION_REQUIRED=YES`: the code, name, dates, and initial status are not recoverable safely from legacy data.
