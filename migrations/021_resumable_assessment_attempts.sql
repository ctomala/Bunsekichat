-- ============================================================
-- BUNSEKICHAT
-- Migration 021
-- P5A6B - Resumable Assessment Attempt Engine
--
-- ADDITIVE ONLY:
--   - Does not modify legacy rows
--   - Does not alter adaptive_quizzes
--   - Does not alter adaptive_questions
--   - Does not alter research_tests
-- ============================================================

CREATE TABLE public.assessment_attempts (
    id BIGSERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL
        REFERENCES public.users(id)
        ON DELETE CASCADE,

    assessment_kind TEXT NOT NULL,

    -- Stable application identifier for the evaluated instrument.
    -- Examples:
    -- adaptive_quiz:135
    -- teacher_assessment:1
    -- research_instrument_version:25
    source_key TEXT NOT NULL,

    adaptive_quiz_id INTEGER NULL
        REFERENCES public.adaptive_quizzes(id)
        ON DELETE CASCADE,

    teacher_assessment_id INTEGER NULL
        REFERENCES public.teacher_assessments(id)
        ON DELETE SET NULL,

    research_test_id INTEGER NULL
        REFERENCES public.research_tests(id)
        ON DELETE SET NULL,

    status TEXT NOT NULL
        DEFAULT 'in_progress',

    started_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    last_activity_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    expires_at TIMESTAMPTZ NULL,

    submitted_at TIMESTAMPTZ NULL,

    current_position INTEGER NOT NULL
        DEFAULT 0,

    resume_count INTEGER NOT NULL
        DEFAULT 0,

    elapsed_seconds INTEGER NOT NULL
        DEFAULT 0,

    version_code TEXT NULL,

    metadata_json JSONB NOT NULL
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT assessment_attempts_kind_check
        CHECK (
            assessment_kind IN (
                'pretest',
                'posttest',
                'adaptive',
                'teacher_assessment',
                'research',
                'practice',
                'other'
            )
        ),

    CONSTRAINT assessment_attempts_status_check
        CHECK (
            status IN (
                'in_progress',
                'submitted',
                'expired',
                'cancelled',
                'abandoned'
            )
        ),

    CONSTRAINT assessment_attempts_current_position_check
        CHECK (current_position >= 0),

    CONSTRAINT assessment_attempts_resume_count_check
        CHECK (resume_count >= 0),

    CONSTRAINT assessment_attempts_elapsed_seconds_check
        CHECK (elapsed_seconds >= 0),

    CONSTRAINT assessment_attempts_source_key_check
        CHECK (BTRIM(source_key) <> '')
);


CREATE TABLE public.assessment_attempt_answers (
    id BIGSERIAL PRIMARY KEY,

    attempt_id BIGINT NOT NULL
        REFERENCES public.assessment_attempts(id)
        ON DELETE CASCADE,

    -- Generic key permits future scientific instruments that
    -- are not backed by adaptive_questions.
    question_key TEXT NOT NULL,

    question_id INTEGER NULL
        REFERENCES public.adaptive_questions(id)
        ON DELETE SET NULL,

    answer_json JSONB NOT NULL
        DEFAULT '{}'::jsonb,

    first_answered_at TIMESTAMPTZ NULL,

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    elapsed_seconds INTEGER NOT NULL
        DEFAULT 0,

    change_count INTEGER NOT NULL
        DEFAULT 0,

    CONSTRAINT assessment_attempt_answers_question_key_check
        CHECK (BTRIM(question_key) <> ''),

    CONSTRAINT assessment_attempt_answers_elapsed_check
        CHECK (elapsed_seconds >= 0),

    CONSTRAINT assessment_attempt_answers_change_count_check
        CHECK (change_count >= 0),

    CONSTRAINT uq_assessment_attempt_answer
        UNIQUE (attempt_id, question_key)
);


-- ------------------------------------------------------------
-- ATTEMPT LOOKUPS / RESUME
-- ------------------------------------------------------------

CREATE INDEX idx_assessment_attempts_user_status
    ON public.assessment_attempts (
        user_id,
        status,
        last_activity_at DESC
    );


CREATE INDEX idx_assessment_attempts_source
    ON public.assessment_attempts (
        assessment_kind,
        source_key
    );


CREATE INDEX idx_assessment_attempts_adaptive_quiz
    ON public.assessment_attempts (
        adaptive_quiz_id
    );


CREATE INDEX idx_assessment_attempts_teacher_assessment
    ON public.assessment_attempts (
        teacher_assessment_id
    );


CREATE INDEX idx_assessment_attempts_research_test
    ON public.assessment_attempts (
        research_test_id
    );


-- One active attempt per student + instrument.
CREATE UNIQUE INDEX uq_assessment_attempts_one_active
    ON public.assessment_attempts (
        user_id,
        assessment_kind,
        source_key
    )
    WHERE status = 'in_progress';


-- Additional protection for current adaptive-quizzes architecture.
CREATE UNIQUE INDEX uq_assessment_attempts_one_active_quiz
    ON public.assessment_attempts (
        user_id,
        adaptive_quiz_id
    )
    WHERE
        status = 'in_progress'
        AND adaptive_quiz_id IS NOT NULL;


-- ------------------------------------------------------------
-- AUTOSAVE LOOKUPS
-- ------------------------------------------------------------

CREATE INDEX idx_assessment_attempt_answers_attempt
    ON public.assessment_attempt_answers (
        attempt_id
    );


CREATE INDEX idx_assessment_attempt_answers_question
    ON public.assessment_attempt_answers (
        question_id
    );


CREATE INDEX idx_assessment_attempt_answers_updated
    ON public.assessment_attempt_answers (
        attempt_id,
        updated_at DESC
    );

-- ============================================================
-- END MIGRATION 021
-- ============================================================
