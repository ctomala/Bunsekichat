# Teacher account plan

Create a new `users` row atomically with username `ctomala.docente`, `role='teacher'`, active account state, bcrypt password hash, and the existing required user fields. The current application explicitly recognizes the `teacher` role; no new role value is required. Receive the temporary password in memory at execution, hash it before the insert, never log it, and never persist plaintext.

Then insert exactly one `teachers` record referring to the new `users.id`. The unique FK prevents duplicate teacher bindings. The existing admin user is neither read as a binding candidate nor modified.

`profiles` is not required by `teachers`, the defined initial structure contains no profile attributes, and current app queries use a left join for profiles. Therefore `PROFILES_CREATED=0` for this execution plan. Any future teacher-profile feature needs a separate explicit field and privacy contract. All three steps run inside the single future transaction; any failure rolls back the user and teacher row together.
