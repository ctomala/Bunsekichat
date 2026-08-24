# Production runbook — BUNSEKI-018A.4B

1. Confirm approved commit, branch, backup existence and SHA-256.
2. Establish controlled connection; record read-only baseline, object conflict and privilege metadata.
3. Abort on SHA mismatch, critical drift/conflict, insufficient privileges, unexpected SQL, seed mismatch, legacy/GPS count change or historical enrollment above zero.
4. Open a transaction; apply `018a3_academic_foundation.sql`; verify tables, exact five seeds, `enrollments=0`, and legacy/GPS counts; commit only when every check passes.
5. On any pre-commit error, issue `ROLLBACK`. Destructive removal of new tables requires separate Founder authorization.
