BEGIN;

ALTER TABLE enrollments
    DROP CONSTRAINT IF EXISTS fk_enrollments_cohort_parallel_course;

ALTER TABLE cohorts
    DROP CONSTRAINT IF EXISTS uq_cohorts_id_parallel_course;

DROP INDEX IF EXISTS idx_cohorts_parallel_id;

ALTER TABLE cohorts
    DROP CONSTRAINT IF EXISTS fk_cohorts_parallel_course;

ALTER TABLE cohorts
    DROP COLUMN IF EXISTS parallel_id;

ALTER TABLE parallels
    DROP CONSTRAINT IF EXISTS uq_parallels_id_course;

COMMIT;
