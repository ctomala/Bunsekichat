-- TEACHER ASSESSMENT TARGETING V3.
-- Additive migration. Do not run against production without an explicit governed gate.

ALTER TABLE teacher_assessments
    ADD COLUMN IF NOT EXISTS audience_mode TEXT NOT NULL DEFAULT 'academic_context'
    CHECK (audience_mode IN ('academic_context','targeted'));

CREATE TABLE IF NOT EXISTS teacher_assessment_targets (
    assessment_id INTEGER NOT NULL REFERENCES teacher_assessments(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (assessment_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_teacher_assessment_targets_user_id
    ON teacher_assessment_targets(user_id);

CREATE INDEX IF NOT EXISTS idx_teacher_assessments_audience_mode
    ON teacher_assessments(audience_mode);
