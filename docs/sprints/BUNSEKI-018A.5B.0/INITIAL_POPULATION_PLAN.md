# Initial population plan

No production action is authorized by this document. The approved initial structure is one teacher user, one teacher entity, one period, five courses, five `teacher_courses` rows, eight parallels, eight cohorts, and zero enrollments. Parallel distribution is CALC-DIF=2, EST=2, ALG=1, ALG-ELEM=1, CALC-INT=2. The approved cohort policy creates one deterministic non-PII cohort per course/parallel tuple.

Pre/post zero-student guarantee: check `enrollments=0` before and after; check `legacy_academic_reconciliation=0`; verify users increase by exactly one and profiles, interactions, location events, and GPS content remain unchanged. No historical user is enrolled or altered.
