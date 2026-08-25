# 018A.5B.1B-P1 preflight closure

`PREFLIGHT=PASS`; schema, uniqueness, password, and production read-only contracts passed. `TRANSACTION_READ_ONLY=on`; teacher username conflict=0; period conflict=0; `teacher_parallels=PRESENT`; rows=0; privileges sufficient; activity risk low.

Certified immediately pre-5B1B backups remain outside the repository: full SHA-256 `18466A8936491885CAEDF749DD408E573BE386D8CD347425A58FCCD946E248A2`, public SHA-256 `504AF312E71BC28DEDB9C4715A268ECF6A4C3E7EEEDC9322F4C0ECE83FD93285`. PostgreSQL 17 public restore passed and preserved the UTF-8 defective baseline.

Future target is one separate teacher, one draft period, five courses, five teacher-course assignments, eight parallels, eight teacher-parallel assignments, eight cohorts, and zero students/enrollments/reconciliation/backfill. UTF-8 repair is ASCII-only `decode`/`convert_from` via `docker cp` plus `psql -f`; password stays local/in-memory and only bcrypt may persist.

`018A.5B.1B=NOT_AUTHORIZED`. This document executes no production SQL, repair, population, backup, or rollback.
