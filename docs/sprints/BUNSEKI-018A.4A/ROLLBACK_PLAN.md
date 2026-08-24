# Rollback plan

`018a4_rollback_academic_foundation.sql` removes only the new academic tables in dependency order. It never touches `users`, `profiles`, interactions, GPS, quizzes, plans or research tables. Use only with Founder authorization; before a production commit, prefer transaction `ROLLBACK` rather than destructive rollback.
