
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
    version_code TEXT,
    dimension_scores_json TEXT,
    diagnosis_json TEXT,
    cognitive_profile TEXT,
    learning_plan_json TEXT,
    total_time_seconds DOUBLE PRECISION,
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
    item_code TEXT,
    position INTEGER,
    topic TEXT,
    subtopic TEXT,
    dimension TEXT,
    indicator TEXT,
    competence TEXT,
    difficulty_level TEXT,
    user_answer TEXT,
    response_time_seconds DOUBLE PRECISION,
    attempts INTEGER DEFAULT 1,
    explanation TEXT,
    bloom_level TEXT,
    conceptual_error TEXT,
    estimated_confidence DOUBLE PRECISION,
    is_correct BOOLEAN
);

CREATE TABLE IF NOT EXISTS research_exercise_attempts(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES adaptive_quizzes(id) ON DELETE SET NULL,
    topic TEXT,
    subtopic TEXT,
    exercise_text TEXT NOT NULL,
    options_json TEXT,
    correct_answer TEXT,
    user_answer TEXT,
    difficulty_level TEXT,
    is_correct BOOLEAN,
    feedback TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_survey_responses(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES adaptive_quizzes(id) ON DELETE SET NULL,
    item_no INTEGER,
    dimension TEXT,
    item_text TEXT,
    score INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_learning_events(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id INTEGER REFERENCES adaptive_quizzes(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    duration_seconds DOUBLE PRECISION,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS subject TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS course_level TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS parallel TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS shift TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS cohort TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS full_name_normalized TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS research_group TEXT DEFAULT 'Sin asignar';
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
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS version_code TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS dimension_scores_json TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS diagnosis_json TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS cognitive_profile TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS learning_plan_json TEXT;
ALTER TABLE IF EXISTS adaptive_quizzes ADD COLUMN IF NOT EXISTS total_time_seconds DOUBLE PRECISION;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS position INTEGER;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS item_code TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS topic TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS subtopic TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS dimension TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS indicator TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS competence TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS difficulty_level TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS response_time_seconds DOUBLE PRECISION;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS attempts INTEGER DEFAULT 1;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS conceptual_error TEXT;
ALTER TABLE IF EXISTS adaptive_questions ADD COLUMN IF NOT EXISTS estimated_confidence DOUBLE PRECISION;

CREATE INDEX IF NOT EXISTS idx_plan_topics_plan_id ON plan_topics(plan_id);
CREATE INDEX IF NOT EXISTS idx_adaptive_quizzes_user_id ON adaptive_quizzes(user_id);
CREATE INDEX IF NOT EXISTS idx_adaptive_quizzes_research ON adaptive_quizzes(quiz_type, subject, course_level, parallel, shift);
CREATE INDEX IF NOT EXISTS idx_adaptive_questions_quiz_id ON adaptive_questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_profiles_cohort ON profiles(cohort);
CREATE INDEX IF NOT EXISTS idx_research_exercise_attempts_user_id ON research_exercise_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_research_survey_user_id ON research_survey_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_research_learning_events_user_id ON research_learning_events(user_id);
