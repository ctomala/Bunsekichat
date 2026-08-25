# Period row contract

| Entity | Column | Value source | Required | Validation |
|---|---|---|---|---|
| academic_periods | code | Founder | yes | unique 2026-2027-CII |
| academic_periods | name | approved manifest | yes | 2026-2027-CII |
| academic_periods | start_date/end_date | Founder | no schema / required plan | ordered dates |
| academic_periods | status | schema | yes | `draft` |

The actual CHECK permits only `draft`, `active`, and `closed`; there is no active boolean. Because the period begins after the current date, `draft` is the correct supported status. `PERIOD_STATUS_CONTRACT=PASS`.
