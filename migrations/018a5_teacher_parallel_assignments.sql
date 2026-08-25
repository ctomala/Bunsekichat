-- BUNSEKI-018A.5. Additive parallel-scoped teacher authorization.
CREATE TABLE IF NOT EXISTS teacher_parallels (
    teacher_id BIGINT NOT NULL REFERENCES teachers(id),
    parallel_id BIGINT NOT NULL REFERENCES parallels(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (teacher_id, parallel_id)
);
CREATE INDEX IF NOT EXISTS idx_teacher_parallels_parallel ON teacher_parallels(parallel_id);
