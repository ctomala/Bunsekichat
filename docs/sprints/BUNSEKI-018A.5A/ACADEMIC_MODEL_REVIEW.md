# Academic model review

Reviewed from `migrations/018a3_academic_foundation.sql`, `bunseki/academic/service.py`, and a PostgreSQL 17 restore of the certified legacy backup with 018a3 applied only locally.

| Entity | Primary key | Foreign keys | Unique rules | Required fields | Optional fields | Lifecycle | Population source |
|---|---|---|---|---|---|---|---|
| teachers | id | user_id → users | user_id | user_id, status | — | active/inactive | explicit existing or new teacher user binding |
| academic_periods | id | — | code | code, name, status | start_date, end_date | draft/active/closed | Founder-approved period manifest |
| subjects | id | — | code, name | code, name, active | description, category | active flag | existing catalog; controlled future catalog change |
| courses | id | subject_id, academic_period_id | (academic_period_id, code); (id, academic_period_id) | subject_id, academic_period_id, code, name, status | — | draft/status policy | approved offering manifest |
| teacher_courses | (teacher_id, course_id) | teacher_id, course_id | composite primary key | teacher_id, course_id, role | — | assignment row | explicit authorization assignment |
| parallels | id | course_id | (course_id, code); (course_id, id) | course_id, code, name, active | — | active flag | approved class-section manifest |
| cohorts | id | course_id | code; (course_id, id) | course_id, code, name, status | research_group | active/status policy | approved analytical-cohort manifest |
| enrollments | id | student_user_id; composite course/parallel and course/cohort links | (student_user_id, cohort_id) | student_user_id, course_id, parallel_id, cohort_id, status, source | — | active/status policy | explicit new or existing-user enrollment contract |
| legacy_academic_reconciliation | id | user_id, enrollment_id | user_id | user_id, status | enrollment_id, reason | pending/reviewed resolution record | explicit reconciliation workflow |

Course is an offering of one subject in one academic period: its direct required FKs establish both dimensions. Parallel and Cohort both belong to Course, but have distinct roles. Enrollment's composite FKs prevent mixing a parallel or cohort from another course.

Indexes explicitly created are `idx_enrollments_student` and `idx_enrollments_course`. No schema constraint enforces period date ordering, date overlap, course status vocabulary, cohort status vocabulary, or a role vocabulary for `teacher_courses`; those remain operational validation requirements before a future write.
