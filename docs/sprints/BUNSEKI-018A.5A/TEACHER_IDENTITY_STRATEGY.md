# Initial teacher identity strategy

`teachers.user_id` is a required, unique FK to `users.id`; the foundation therefore supports a single existing application identity per teacher record and does not require a second student-like identity.

The current application admits `admin`, `teacher`, and `docente` roles to the broad teacher/admin dashboard, which reads legacy profile fields. It does not consume `teachers` or `teacher_courses`. The sole existing admin account is consequently not demonstrated to be the initial teacher.

`INITIAL_TEACHER_IDENTITY_STRATEGY=FOUNDER_DECISION_REQUIRED`.

Before 018A.5B, the Founder must choose either an explicitly identified existing user to bind, after role/authorization review, or approve creation of a distinct teacher user through a separately authorized account lifecycle. Binding the existing admin merely because it is the only non-student account is forbidden. A future UI integration must resolve course access through `teachers → teacher_courses`, deny access when no assignment exists, and never trust the legacy textual `profiles.teacher` field as authorization.
