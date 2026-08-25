-- DO NOT RUN WITHOUT FOUNDER AUTHORIZATION.
-- Rolls back only the structure introduced by 018a5_teacher_parallel_assignments.sql.
BEGIN;
DROP TABLE IF EXISTS teacher_parallels;
COMMIT;
