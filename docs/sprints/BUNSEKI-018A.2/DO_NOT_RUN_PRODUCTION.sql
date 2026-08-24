-- DO NOT RUN IN PRODUCTION. Draft only; BUNSEKI-018A.2 did not execute this file.
-- Future BUNSEKI-018A.3: run only after backup, review and dedicated test validation.
BEGIN;
CREATE TABLE teachers (user_id INTEGER PRIMARY KEY REFERENCES users(id), created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE academic_periods (id BIGSERIAL PRIMARY KEY, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL, starts_on DATE, ends_on DATE, status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','active','closed')), created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE subjects (id BIGSERIAL PRIMARY KEY, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL UNIQUE, active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE courses (id BIGSERIAL PRIMARY KEY, academic_period_id BIGINT NOT NULL REFERENCES academic_periods(id), subject_id BIGINT NOT NULL REFERENCES subjects(id), UNIQUE(academic_period_id,subject_id));
CREATE TABLE teacher_courses (teacher_user_id INTEGER NOT NULL REFERENCES teachers(user_id), course_id BIGINT NOT NULL REFERENCES courses(id), PRIMARY KEY(teacher_user_id,course_id));
CREATE TABLE parallels (id BIGSERIAL PRIMARY KEY, course_id BIGINT NOT NULL REFERENCES courses(id), code TEXT NOT NULL, UNIQUE(course_id,code));
CREATE TABLE cohorts (id BIGSERIAL PRIMARY KEY, parallel_id BIGINT NOT NULL REFERENCES parallels(id), code TEXT NOT NULL UNIQUE, name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active', created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE enrollments (id BIGSERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), cohort_id BIGINT NOT NULL REFERENCES cohorts(id), research_group TEXT, status TEXT NOT NULL DEFAULT 'active', enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(), ended_at TIMESTAMPTZ, UNIQUE(user_id,cohort_id));
CREATE INDEX idx_enrollments_user ON enrollments(user_id); CREATE INDEX idx_enrollments_cohort ON enrollments(cohort_id);
-- Do not backfill here. Do not commit this transaction in a future execution until reviewed.
ROLLBACK;
