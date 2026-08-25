# Teacher account contract

Required `users` fields: `username`, `password_hash`, `role`, `active`, `created_at`, `password_temporal`, `primer_ingreso`. Use `role='teacher'`, which current app authorization accepts. `teachers.user_id` is required, unique, and references `users.id`. A profile is not structurally required; planned profile rows: zero.

The established application-compatible mechanism is bcrypt (`hash_password` / `bcrypt.hashpw`). The admin account is never updated. `PASSWORD_PLAINTEXT_PERSISTENCE=0`.
