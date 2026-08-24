# 018A.5B population runbook draft

This is a draft only; it grants no production authority.

1. Receive explicit Founder authorization and a validated manifest.
2. Verify branch/revision, backup/current aggregate baseline, write authority, schema objects, and no conflicting activity.
3. Begin one transaction with bounded lock and statement timeouts.
4. Bind the approved teacher identity (or execute separately approved user lifecycle).
5. Insert the approved academic period.
6. Insert approved course offerings using existing subjects.
7. Insert `teacher_courses` assignments.
8. Insert parallels and cohorts, validating their course relation.
9. Validate all structure and authorization paths; execute only explicitly approved new/existing enrollments.
10. Re-read aggregate/object results, then commit only if every validation passes.

Any validation failure rolls back the transaction. Do not use global DROP or a destructive cleanup. Historical enrollments are excluded unless separately and explicitly authorized. The execution may validly finish with zero enrollments.
