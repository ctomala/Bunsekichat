BEGIN;

-- BUNSEKI-018A.6
-- Cohort -> Parallel integrity.
-- Fail closed: existing cohorts must be either zero (fresh DB)
-- or exactly the certified first production population.

LOCK TABLE parallels IN SHARE ROW EXCLUSIVE MODE;
LOCK TABLE cohorts IN SHARE ROW EXCLUSIVE MODE;
LOCK TABLE enrollments IN SHARE ROW EXCLUSIVE MODE;

ALTER TABLE cohorts
    ADD COLUMN IF NOT EXISTS parallel_id BIGINT;


-- Allows a composite FK that proves that a parallel belongs
-- to the same course stored in cohorts.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'public.parallels'::regclass
          AND conname = 'uq_parallels_id_course'
    ) THEN
        ALTER TABLE parallels
            ADD CONSTRAINT uq_parallels_id_course
            UNIQUE (id, course_id);
    END IF;
END
$$;


-- Validate the existing population BEFORE backfill.
DO $$
DECLARE
    cohort_total INTEGER;
    matched_total INTEGER;
BEGIN
    -- If every existing cohort is already mapped, the migration has
    -- already been applied successfully. This also allows safe
    -- re-execution after future cohorts have been created.
    IF NOT EXISTS (
        SELECT 1
        FROM cohorts
        WHERE parallel_id IS NULL
    ) THEN
        RETURN;
    END IF;

    SELECT COUNT(*)
      INTO cohort_total
      FROM cohorts;

    SELECT COUNT(*)
      INTO matched_total
      FROM cohorts c
      JOIN (
          VALUES
              (1::BIGINT, 1::BIGINT, 1::BIGINT,
               '2026-2027-CII-CALC-DIF-PMF-MA-4-A1', 'A1'),
              (2::BIGINT, 1::BIGINT, 2::BIGINT,
               '2026-2027-CII-CALC-DIF-PMF-MA-4-A2', 'A2'),
              (3::BIGINT, 2::BIGINT, 3::BIGINT,
               '2026-2027-CII-EST-PMF-MA-3-3A1', '3A1'),
              (4::BIGINT, 2::BIGINT, 4::BIGINT,
               '2026-2027-CII-EST-PMF-MA-3-3A2', '3A2'),
              (5::BIGINT, 3::BIGINT, 5::BIGINT,
               '2026-2027-CII-ALG-PMF-MA-5-5A1', '5A1'),
              (6::BIGINT, 4::BIGINT, 6::BIGINT,
               '2026-2027-CII-ALG-ELEM-PMF-MA-2-2A1', '2A1'),
              (7::BIGINT, 5::BIGINT, 7::BIGINT,
               '2026-2027-CII-CALC-INT-PMF-MA-5C-5C1', '5C1'),
              (8::BIGINT, 5::BIGINT, 8::BIGINT,
               '2026-2027-CII-CALC-INT-PMF-MA-5C-5C2', '5C2')
      ) AS expected(
          cohort_id,
          course_id,
          parallel_id,
          cohort_code,
          parallel_code
      )
        ON c.id = expected.cohort_id
       AND c.course_id = expected.course_id
       AND c.code = expected.cohort_code
      JOIN parallels p
        ON p.id = expected.parallel_id
       AND p.course_id = expected.course_id
       AND p.code = expected.parallel_code;

    IF cohort_total <> 8 THEN
        RAISE EXCEPTION
            '018a6 blocked: expected 8 unmapped certified cohorts, found %',
            cohort_total;

    ELSIF matched_total <> 8 THEN
        RAISE EXCEPTION
            '018a6 blocked: certified cohort/parallel map matched % of 8',
            matched_total;
    END IF;
END
$$;


-- Explicit certified backfill.
WITH mapping(cohort_id, course_id, parallel_id) AS (
    VALUES
        (1::BIGINT, 1::BIGINT, 1::BIGINT),
        (2::BIGINT, 1::BIGINT, 2::BIGINT),
        (3::BIGINT, 2::BIGINT, 3::BIGINT),
        (4::BIGINT, 2::BIGINT, 4::BIGINT),
        (5::BIGINT, 3::BIGINT, 5::BIGINT),
        (6::BIGINT, 4::BIGINT, 6::BIGINT),
        (7::BIGINT, 5::BIGINT, 7::BIGINT),
        (8::BIGINT, 5::BIGINT, 8::BIGINT)
)
UPDATE cohorts c
   SET parallel_id = mapping.parallel_id
  FROM mapping
 WHERE c.id = mapping.cohort_id
   AND c.course_id = mapping.course_id
   AND c.parallel_id IS NULL;


-- Database-level proof:
-- cohort.parallel_id and cohort.course_id must describe
-- the same row in parallels.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'public.cohorts'::regclass
          AND conname = 'fk_cohorts_parallel_course'
    ) THEN
        ALTER TABLE cohorts
            ADD CONSTRAINT fk_cohorts_parallel_course
            FOREIGN KEY (parallel_id, course_id)
            REFERENCES parallels (id, course_id)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
            NOT VALID;
    END IF;
END
$$;

ALTER TABLE cohorts
    VALIDATE CONSTRAINT fk_cohorts_parallel_course;


-- No cohort may remain ambiguous.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM cohorts
        WHERE parallel_id IS NULL
    ) THEN
        RAISE EXCEPTION
            '018a6 blocked: cohort without parallel_id remains';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM cohorts c
        LEFT JOIN parallels p
          ON p.id = c.parallel_id
         AND p.course_id = c.course_id
        WHERE p.id IS NULL
    ) THEN
        RAISE EXCEPTION
            '018a6 blocked: cohort/course/parallel mismatch detected';
    END IF;
END
$$;

ALTER TABLE cohorts
    ALTER COLUMN parallel_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_cohorts_parallel_id
    ON cohorts (parallel_id);


-- Enables exact enrollment integrity:
-- enrollment.course + parallel + cohort must describe
-- the same academic context.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'public.cohorts'::regclass
          AND conname = 'uq_cohorts_id_parallel_course'
    ) THEN
        ALTER TABLE cohorts
            ADD CONSTRAINT uq_cohorts_id_parallel_course
            UNIQUE (id, parallel_id, course_id);
    END IF;
END
$$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'public.enrollments'::regclass
          AND conname = 'fk_enrollments_cohort_parallel_course'
    ) THEN
        ALTER TABLE enrollments
            ADD CONSTRAINT fk_enrollments_cohort_parallel_course
            FOREIGN KEY (cohort_id, parallel_id, course_id)
            REFERENCES cohorts (id, parallel_id, course_id)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
            NOT VALID;
    END IF;
END
$$;

ALTER TABLE enrollments
    VALIDATE CONSTRAINT fk_enrollments_cohort_parallel_course;


-- Final migration assertions.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM cohorts c
        JOIN parallels p
          ON p.id = c.parallel_id
        WHERE c.course_id <> p.course_id
    ) THEN
        RAISE EXCEPTION
            '018a6 final validation failed: cross-course cohort';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM enrollments e
        JOIN cohorts c
          ON c.id = e.cohort_id
        WHERE e.parallel_id <> c.parallel_id
           OR e.course_id <> c.course_id
    ) THEN
        RAISE EXCEPTION
            '018a6 final validation failed: inconsistent enrollment';
    END IF;
END
$$;

COMMIT;
