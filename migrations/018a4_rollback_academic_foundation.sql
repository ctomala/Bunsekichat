-- DO NOT RUN WITHOUT FOUNDER AUTHORIZATION.
-- Removes only BUNSEKI-018A Academic Foundation structures; never legacy data.
BEGIN;
DROP TABLE IF EXISTS teacher_courses;
DROP TABLE IF EXISTS legacy_academic_reconciliation;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS cohorts;
DROP TABLE IF EXISTS parallels;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS academic_periods;
COMMIT;
