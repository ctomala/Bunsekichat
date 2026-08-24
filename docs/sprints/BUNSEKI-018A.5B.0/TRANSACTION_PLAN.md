# 018A.5B.1 transaction plan

This is a future execution design, not executable authorization.

1. Precheck approved branch/revision, certified backup, production activity, subject catalog, teacher-username availability, Academic Foundation state, and legacy aggregate fingerprints.
2. Begin one transaction with bounded lock and statement timeouts.
3. Normalize only ALG display name from `Álgebra` to `Álgebra Lineal`.
4. Receive temporary password only in memory; generate bcrypt before SQL through a secure service contract. Never echo it, write it to temporary SQL, log it, or persist it. Insert exactly one distinct `teacher`-role user and its `teachers` binding.
5. Insert approved `draft` period `2026-2027-CII` with dates `2026-10-01` through `2027-02-25`.
6. Insert five course offerings, five assignments, eight confirmed parallels, and eight deterministic non-PII cohorts.
7. Insert no enrollments and no reconciliation rows.
8. Validate: admin unchanged; one teacher user/entity and period; five subjects/courses/assignments; eight parallels/cohorts; correct ALG name; zero enrollments/reconciliation; unchanged legacy and GPS fingerprints; zero plaintext-password persistence.
9. Commit only if every validation passes; otherwise rollback the entire transaction.

Rollback is transactional; no global DROP, delete, or cleanup is permitted.
