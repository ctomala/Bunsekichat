# Validation plan for 018A.5B.1

Required post-transaction checks: `TEACHER_USER_CREATED=1`; `TEACHER_ENTITY_CREATED=1`; `ACADEMIC_PERIODS_CREATED=1`; `COURSES_CREATED=5`; `TEACHER_COURSES_CREATED=5`; `PARALLELS_CREATED=8`; `COHORTS_CREATED=8`; `ENROLLMENTS=0`; `LEGACY_RECONCILIATION=0`; five existing subjects; and ALG display name `Álgebra Lineal`.

Users must increase by exactly one (the teacher account). Profiles must increase by zero under the approved account contract. Interactions, location events, historical user rows, and GPS content must be unchanged. Validate that each parallel and cohort resolves to its declared course and that the teacher has one assignment for every created course. Verify no row contains the runtime password value; only its bcrypt hash may persist.

Precheck rejects a teacher username conflict, missing subject, unexpected Academic Foundation state, or fingerprint mismatch. All validation failures roll back.
