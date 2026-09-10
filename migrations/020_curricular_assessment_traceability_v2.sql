-- CURRICULAR ASSESSMENT TRACEABILITY V2. Additive; do not run without approval.
CREATE TABLE IF NOT EXISTS teacher_assessments (
 id SERIAL PRIMARY KEY, created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
 plan_id INTEGER NOT NULL REFERENCES analytic_plans(id) ON DELETE RESTRICT, title TEXT NOT NULL,
 subject TEXT, course_level TEXT, parallel TEXT, shift TEXT, cohort TEXT,
 status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','published','closed')),
 created_at TEXT NOT NULL, published_at TEXT, closed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_teacher_assessments_created_by ON teacher_assessments(created_by);
CREATE INDEX IF NOT EXISTS idx_teacher_assessments_plan_id ON teacher_assessments(plan_id);
CREATE INDEX IF NOT EXISTS idx_teacher_assessments_status ON teacher_assessments(status);
CREATE INDEX IF NOT EXISTS idx_teacher_assessments_subject ON teacher_assessments(subject);
CREATE INDEX IF NOT EXISTS idx_teacher_assessments_course_level ON teacher_assessments(course_level);
CREATE INDEX IF NOT EXISTS idx_teacher_assessments_parallel ON teacher_assessments(parallel);
CREATE TABLE IF NOT EXISTS teacher_assessment_items (
 id SERIAL PRIMARY KEY, assessment_id INTEGER NOT NULL REFERENCES teacher_assessments(id) ON DELETE CASCADE,
 question_bank_item_id INTEGER NOT NULL REFERENCES question_bank_items(id) ON DELETE RESTRICT,
 position INTEGER NOT NULL, UNIQUE(assessment_id,question_bank_item_id), UNIQUE(assessment_id,position)
);
CREATE INDEX IF NOT EXISTS idx_teacher_assessment_items_assessment_id ON teacher_assessment_items(assessment_id);
CREATE INDEX IF NOT EXISTS idx_teacher_assessment_items_bank_item_id ON teacher_assessment_items(question_bank_item_id);
ALTER TABLE adaptive_quizzes ADD COLUMN IF NOT EXISTS teacher_assessment_id INTEGER REFERENCES teacher_assessments(id) ON DELETE SET NULL;
ALTER TABLE adaptive_questions ADD COLUMN IF NOT EXISTS question_bank_item_id INTEGER REFERENCES question_bank_items(id) ON DELETE SET NULL;
ALTER TABLE adaptive_questions ADD COLUMN IF NOT EXISTS plan_topic_id INTEGER REFERENCES plan_topics(id) ON DELETE SET NULL;
ALTER TABLE adaptive_questions ADD COLUMN IF NOT EXISTS learning_outcome TEXT;
CREATE INDEX IF NOT EXISTS idx_adaptive_quizzes_teacher_assessment ON adaptive_quizzes(teacher_assessment_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_adaptive_quizzes_teacher_assessment_student ON adaptive_quizzes(teacher_assessment_id,user_id) WHERE teacher_assessment_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_adaptive_questions_bank_item ON adaptive_questions(question_bank_item_id);
CREATE INDEX IF NOT EXISTS idx_adaptive_questions_plan_topic ON adaptive_questions(plan_topic_id);
