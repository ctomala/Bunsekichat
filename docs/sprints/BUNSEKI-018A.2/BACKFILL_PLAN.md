# Backfill plan

1. Create additive structures and a migration ledger.
2. Seed approved subjects and create periods/courses/parallels/cohorts only from approved mappings.
3. Normalize candidate values in a staging query/table; never overwrite `profiles`.
4. Insert enrollments only for Founder-approved, unambiguous mappings.
5. Place all remaining records in a manual-review queue with reason codes.
6. Validate counts/FKs and activate dual-read.
7. Use Enrollment for new imports in an all-or-nothing transaction.
8. Retire free-text input only after compatibility validation; retain legacy fields through the agreed retention window.

No backfill was executed in this sprint.
