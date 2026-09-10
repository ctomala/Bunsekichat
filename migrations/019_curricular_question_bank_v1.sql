-- CURRICULAR QUESTION BANK V1. Additive migration; do not run against production without approval.
CREATE TABLE IF NOT EXISTS question_bank_items (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES analytic_plans(id) ON DELETE CASCADE,
    plan_topic_id INTEGER NOT NULL REFERENCES plan_topics(id) ON DELETE CASCADE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    question TEXT NOT NULL,
    options_json TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    unit_name TEXT,
    topic TEXT NOT NULL,
    subtopic TEXT,
    learning_outcome TEXT,
    bloom_level TEXT,
    difficulty_level TEXT,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'rejected', 'deleted')),
    source TEXT NOT NULL DEFAULT 'ai',
    ai_model TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    approved_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_question_bank_items_plan_id ON question_bank_items(plan_id);
CREATE INDEX IF NOT EXISTS idx_question_bank_items_plan_topic_id ON question_bank_items(plan_topic_id);
CREATE INDEX IF NOT EXISTS idx_question_bank_items_status ON question_bank_items(status);
CREATE INDEX IF NOT EXISTS idx_question_bank_items_created_by ON question_bank_items(created_by);
