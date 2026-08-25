# Execution encoding hardening

`UNICODE_WRITE_STRATEGY=PASS`: future 5B.1B SQL is ASCII-only and uses PostgreSQL Unicode escapes for all non-ASCII literals. Do not send Unicode literals through a PowerShell native-process pipe. Any future non-ASCII teacher/profile/course/parallel/cohort display value must use the same Unicode-escape or validated UTF-8-file strategy. Password handling remains independent: plaintext stays only in memory and only a bcrypt hash reaches SQL.
