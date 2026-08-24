# Teacher isolation audit

| Function/page | Resource | Current scope | Required scope | Risk |
|---|---|---|---|---|
| `get_teacher_tables()` | users, profiles, interactions, quizzes | global | teacher's courses/enrollments | Critical |
| Dashboard docente | charts/GPS | global rows after UI text filters | ownership join enforced in SQL | Critical |
| Exportación | student reports | global selectable students | enrolled students only | Critical |
| Seguimiento individual | profiles/interactions | global selectable students | enrolled students only | Critical |
| Datos completos | CSV/GPS exports | global | admin only or teacher-owned scope | Critical |
| Plan manager | analytic plans | not filtered by `teacher_id` | creator/assignment scope | High |

The real database has no `teacher` users: roles are 170 `student`, 1 `admin`. `profiles.teacher` is text, not a relationship. The next implementation must introduce `teachers(user_id)` plus teacher-course assignment and use SQL-level scope predicates; UI filters are not authorization.
