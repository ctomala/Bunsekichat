# Supabase inventory — read-only verified

`DATABASE_URL_PRESENT=true`. BunsekiChat uses `psycopg2` in `app.py`, loading `DATABASE_URL` from Streamlit secrets or `.env`; it does not use Supabase Python/Auth/Storage APIs directly. The audit used a separate connection forced with `default_transaction_read_only=on`; the server returned `transaction_read_only=on` before every query. No connection string or secret was emitted.

Relevant real public tables (row counts): `users` 171, `profiles` 170, `interactions` 734, `location_events` 937, `quizzes` 96, `adaptive_quizzes` 134, `adaptive_questions` 2,670, `research_exercise_attempts` 1,950, `research_survey_responses` 870, `research_learning_events` 248, `research_tests` 8, `research_surveys` 84, `research_learning_logs` 63, `research_consents` 6, `research_cohorts` 1, bulk batches 2 / rows 49. `analytic_plans` and `plan_topics` exist but have zero rows.

Identity graph: `public.users.id` is the integer PK and `username` is unique. `profiles.user_id` is both PK and FK to `users.id`. Interactions, location events, quizzes, adaptive quizzes and research events join to this integer ID. Profiles has partial unique indexes for nonblank `cedula` and case-insensitive `correo`.

Academic graph today is textual. `research_cohorts.code` is a text PK; bulk batches reference it. There are no `teachers`, `subjects`, `academic_periods`, `courses`, `parallels`, `cohorts` or `enrollments` relations. Extra platform schemas (`auth`, `storage`, `realtime`, `vault`) were observed but not read for data; no Supabase Auth or Storage was changed.
