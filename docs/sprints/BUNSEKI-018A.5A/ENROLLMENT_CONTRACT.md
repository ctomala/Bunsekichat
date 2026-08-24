# Enrollment contracts and conflict policy

## New student bulk import

The current service requires `student_code`, `first_name`, `last_name`, `email`, and `username`, creates a bcrypt hash only, and returns a generated temporary password only in memory. The future import manifest must additionally identify the already-approved academic context: `subject_code`, `academic_period_code`, `course_code`, `parallel_code`, and `cohort_code`. The resolver derives database IDs only after validating the subject/period/course relation, parallel/course relation, cohort/course relation, and teacher authorization.

Required: identity fields above; temporary password supplied or generated transiently; academic context; approved source. Optional: only profile fields explicitly needed by the account workflow. Derived: all numeric IDs, enrollment timestamps, password hash. Forbidden: persisted plaintext passwords, GPS, unnecessary PII, academic inference, and teacher inference.

## Existing-user enrollment

Use the existing `users.id`; never create a second account. Preflight must verify existence, permitted student role, course existence, course membership of parallel and cohort, valid cohort context, assigned/authorized teacher, and no duplicate active enrollment. It must write only under a separately authorized 018A.5B transaction.

## Duplicate and conflict policy

| Case | Policy |
|---|---|
| duplicate username | REJECTED |
| duplicate enrollment in same cohort | REJECTED (database unique rule) |
| student already in another parallel of same course | REQUIRES_EXPLICIT_TRANSFER |
| student in multiple subjects | ALLOWED when separately valid enrollments exist |
| student in multiple periods | ALLOWED when period and lifecycle rules permit |
| same cohort across parallels | REQUIRES_MANUAL_REVIEW; cohort is course-scoped, not a synonym for section |
| course reassignment | REQUIRES_EXPLICIT_TRANSFER |
| teacher reassignment | REQUIRES_EXPLICIT_TRANSFER with authorization review |
