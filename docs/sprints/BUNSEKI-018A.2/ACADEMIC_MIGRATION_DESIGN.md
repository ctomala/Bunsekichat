# Academic migration design

Use `users` as the identity root; do not duplicate `profiles` into a new student record initially. Add `teachers(user_id PK FK users)`, `academic_periods`, `subjects`, `courses(period_id, subject_id)`, `parallels(course_id)`, `cohorts(parallel_id)` and `enrollments(user_id, cohort_id)`. Add teacher-course assignments. `enrollments` carries status, research group and history.

Legacy `profiles` remains untouched. New queries dual-read the enrollment when it exists and fall back to legacy text for historical display only. Initial subject seeds are data rows: Álgebra Elemental / Precálculo, Álgebra, Estadística, Cálculo Diferencial and Cálculo Integral. Curriculum is later versioned under subject; units/topics/skills and prerequisite edges remain separate from enrollment.

Research sources already available include interactions, quizzes, adaptive quizzes/questions, exercises, surveys and learning events, all tied to `users.id`. A future research view should derive a stable pseudonym and exclude profile PII and exact GPS.
