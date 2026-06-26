
-- BunsekiChat: módulo de planes analíticos y evaluación adaptativa IA
CREATE TABLE IF NOT EXISTS analytic_plans(
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    course TEXT,
    subject TEXT,
    course_level TEXT,
    parallel TEXT,
    shift TEXT,
    teacher_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    filename TEXT,
    raw_text TEXT,
    summary TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plan_topics(
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES analytic_plans(id) ON DELETE CASCADE,
    unit_name TEXT,
    topic TEXT,
    subtopic TEXT,
    learning_outcome TEXT,
    bloom_level TEXT,
    keywords TEXT
);

CREATE TABLE IF NOT EXISTS adaptive_quizzes(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER REFERENCES analytic_plans(id) ON DELETE SET NULL,
    title TEXT,
    quiz_type TEXT DEFAULT 'adaptive',
    source_topic TEXT,
    difficulty TEXT,
    subject TEXT,
    course_level TEXT,
    parallel TEXT,
    shift TEXT,
    cohort TEXT,
    research_title TEXT,
    question_count INTEGER,
    random_seed TEXT,
    score DOUBLE PRECISION,
    passed BOOLEAN DEFAULT FALSE,
    attempt_no INTEGER DEFAULT 1,
    parent_quiz_id INTEGER,
    status TEXT DEFAULT 'generated',
    recommendation TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS adaptive_questions(
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL REFERENCES adaptive_quizzes(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    options_json TEXT,
    correct_answer TEXT,
    position INTEGER,
    topic TEXT,
    user_answer TEXT,
    explanation TEXT,
    bloom_level TEXT,
    is_correct BOOLEAN
);

ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS subject TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS course_level TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS parallel TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS shift TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS cohort TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS full_name_normalized TEXT;
ALTER TABLE IF EXISTS analytic_plans ADD COLUMN IF NOT EXISTS subject TEXT;
ALTER TABLE IF EXISTS analytic_plans ADD COLUMN IF NOT EXISTS course_level TEXT;
ALTER TABLE IF EXISTS analytic_plans ADD COLUMN IF NOT EXISTS parallel TEXT;
ALTER TABLE IF EXISTS analytic_plans ADD COLUMN IF NOT EXISTS shift TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS quiz_type TEXT DEFAULT 'adaptive';
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS subject TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS course_level TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS parallel TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS shift TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS cohort TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS research_title TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS question_count INTEGER;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS random_seed TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS position INTEGER;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS topic TEXT;

CREATE INDEX IF NOT EXISTS idx_plan_topics_plan_id ON plan_topics(plan_id);
CREATE INDEX IF NOT EXISTS idx_adaptive_quizzes_user_id ON adaptive_quizzes(user_id);
CREATE INDEX IF NOT EXISTS idx_adaptive_quizzes_research ON adaptive_quizzes(quiz_type, subject, course_level, parallel, shift);
CREATE INDEX IF NOT EXISTS idx_adaptive_questions_quiz_id ON adaptive_questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_profiles_cohort ON profiles(cohort);
