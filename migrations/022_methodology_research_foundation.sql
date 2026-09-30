-- BUNSEKICHAT R8.22B V2
-- MBADA v1.0 + Research + Causal/Predictive Analytics Foundation
-- Creates new structures only. No historical rows are modified.

CREATE TABLE plan_topic_methodologies (
    id BIGSERIAL PRIMARY KEY,
    plan_topic_id INTEGER NOT NULL REFERENCES plan_topics(id) ON DELETE RESTRICT,

    framework_code TEXT NOT NULL DEFAULT 'MBADA',
    framework_version TEXT NOT NULL DEFAULT '1.0',
    version_no INTEGER NOT NULL CHECK (version_no >= 1),

    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','reviewed','approved','retired')),

    pedagogical_objective TEXT,
    prerequisites_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    essential_concepts_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    guiding_question TEXT,

    diagnostic_strategy TEXT,
    explore_strategy TEXT,
    understand_strategy TEXT,
    explain_strategy TEXT,

    worked_example TEXT,
    socratic_prompts_json JSONB NOT NULL DEFAULT '[]'::jsonb,

    practice_strategy TEXT,
    mastery_threshold NUMERIC(5,2) NOT NULL DEFAULT 80.00
        CHECK (mastery_threshold >= 0 AND mastery_threshold <= 100),

    ascend_rule TEXT,
    demonstrate_strategy TEXT,
    transfer_activity TEXT,
    recovery_strategy TEXT,
    reflection_prompt TEXT,

    spacing_plan_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    teacher_notes TEXT,

    ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
    ai_model TEXT,
    prompt_version TEXT,

    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ,

    UNIQUE(plan_topic_id, version_no)
);

CREATE INDEX idx_ptm_topic_status
    ON plan_topic_methodologies(plan_topic_id, status);

COMMENT ON TABLE plan_topic_methodologies IS
    'Versioned teacher-approved MBADA methodology linked to canonical plan topics.';


CREATE TABLE research_protocols (
    id BIGSERIAL PRIMARY KEY,

    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    plan_id INTEGER NOT NULL REFERENCES analytic_plans(id) ON DELETE RESTRICT,

    research_cohort_code TEXT,
    design_type TEXT NOT NULL DEFAULT 'quasi_experimental_prepost',
    methodology_framework TEXT NOT NULL DEFAULT 'MBADA',
    methodology_framework_version TEXT NOT NULL DEFAULT '1.0',

    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','active','closed','archived')),

    pretest_required BOOLEAN NOT NULL DEFAULT TRUE,
    posttest_requires_intervention_complete BOOLEAN NOT NULL DEFAULT TRUE,
    control_exposure_allowed BOOLEAN NOT NULL DEFAULT FALSE,

    pretest_version_code TEXT,
    posttest_version_code TEXT,
    retention_followup_days INTEGER
        CHECK (retention_followup_days IS NULL OR retention_followup_days >= 0),

    causal_question TEXT,
    primary_outcome TEXT,
    treatment_definition TEXT,

    adjustment_set_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    causal_dag_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    analysis_plan_json JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ,

    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_research_protocols_plan_status
    ON research_protocols(plan_id, status);

COMMENT ON TABLE research_protocols IS
    'Versioned study protocol including pre/post rules, treatment definition and causal assumptions.';


CREATE TABLE research_interventions (
    id BIGSERIAL PRIMARY KEY,

    protocol_id BIGINT NOT NULL REFERENCES research_protocols(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plan_id INTEGER NOT NULL REFERENCES analytic_plans(id) ON DELETE RESTRICT,

    research_group TEXT NOT NULL
        CHECK (LOWER(research_group) IN ('experimental','control')),

    status TEXT NOT NULL DEFAULT 'pending_pretest'
        CHECK (status IN (
            'pending_pretest',
            'ready',
            'in_progress',
            'completed',
            'posttest_unlocked',
            'closed',
            'excluded'
        )),

    pretest_quiz_id INTEGER REFERENCES adaptive_quizzes(id) ON DELETE SET NULL,
    pretest_completed_at TIMESTAMPTZ,

    intervention_started_at TIMESTAMPTZ,
    intervention_completed_at TIMESTAMPTZ,
    posttest_unlocked_at TIMESTAMPTZ,

    posttest_quiz_id INTEGER REFERENCES adaptive_quizzes(id) ON DELETE SET NULL,
    posttest_completed_at TIMESTAMPTZ,

    exposure_seconds DOUBLE PRECISION NOT NULL DEFAULT 0
        CHECK (exposure_seconds >= 0),

    protocol_deviation BOOLEAN NOT NULL DEFAULT FALSE,
    contamination_flag BOOLEAN NOT NULL DEFAULT FALSE,
    exclusion_reason TEXT,

    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,

    UNIQUE(protocol_id, user_id)
);

CREATE INDEX idx_research_interventions_protocol_status
    ON research_interventions(protocol_id, status);

CREATE INDEX idx_research_interventions_user
    ON research_interventions(user_id);

CREATE INDEX idx_research_interventions_group
    ON research_interventions(protocol_id, research_group);

COMMENT ON TABLE research_interventions IS
    'Per-student pretest-intervention-posttest state with exposure and protocol integrity.';


CREATE TABLE research_intervention_events (
    id BIGSERIAL PRIMARY KEY,

    intervention_id BIGINT NOT NULL REFERENCES research_interventions(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,

    plan_topic_id INTEGER REFERENCES plan_topics(id) ON DELETE SET NULL,
    methodology_id BIGINT REFERENCES plan_topic_methodologies(id) ON DELETE SET NULL,

    parent_event_id BIGINT REFERENCES research_intervention_events(id) ON DELETE SET NULL,
    sequence_no BIGINT,

    event_type TEXT NOT NULL,

    event_stage TEXT NOT NULL
        CHECK (event_stage IN (
            'protocol',
            'pretest',
            'diagnostic',
            'explore',
            'understand',
            'explain',
            'practice',
            'ascend',
            'demonstrate',
            'recover',
            'reflect',
            'control',
            'posttest',
            'system'
        )),

    event_value_numeric DOUBLE PRECISION,

    duration_seconds DOUBLE PRECISION
        CHECK (duration_seconds IS NULL OR duration_seconds >= 0),

    attempt_no INTEGER
        CHECK (attempt_no IS NULL OR attempt_no >= 0),

    success BOOLEAN,
    difficulty_level TEXT,

    mastery_before NUMERIC(5,2)
        CHECK (mastery_before IS NULL OR
               (mastery_before >= 0 AND mastery_before <= 100)),

    mastery_after NUMERIC(5,2)
        CHECK (mastery_after IS NULL OR
               (mastery_after >= 0 AND mastery_after <= 100)),

    confidence_before NUMERIC(5,2)
        CHECK (confidence_before IS NULL OR
               (confidence_before >= 0 AND confidence_before <= 100)),

    confidence_after NUMERIC(5,2)
        CHECK (confidence_after IS NULL OR
               (confidence_after >= 0 AND confidence_after <= 100)),

    hint_count INTEGER NOT NULL DEFAULT 0 CHECK (hint_count >= 0),
    feedback_count INTEGER NOT NULL DEFAULT 0 CHECK (feedback_count >= 0),

    conceptual_error TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rie_intervention_time
    ON research_intervention_events(intervention_id, occurred_at);

CREATE INDEX idx_rie_user_time
    ON research_intervention_events(user_id, occurred_at);

CREATE INDEX idx_rie_topic
    ON research_intervention_events(plan_topic_id);

CREATE INDEX idx_rie_stage
    ON research_intervention_events(event_stage);

COMMENT ON TABLE research_intervention_events IS
    'Fine-grained temporal learning trace for intervention, mastery, causal and predictive analytics.';


CREATE TABLE student_topic_mastery (
    id BIGSERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plan_topic_id INTEGER NOT NULL REFERENCES plan_topics(id) ON DELETE RESTRICT,
    methodology_id BIGINT NOT NULL REFERENCES plan_topic_methodologies(id) ON DELETE RESTRICT,
    intervention_id BIGINT REFERENCES research_interventions(id) ON DELETE SET NULL,

    mastery_state TEXT NOT NULL DEFAULT 'not_started'
        CHECK (mastery_state IN (
            'not_started',
            'diagnostic',
            'developing',
            'proficient',
            'mastered',
            'recovery'
        )),

    diagnostic_score NUMERIC(5,2)
        CHECK (diagnostic_score IS NULL OR
               (diagnostic_score >= 0 AND diagnostic_score <= 100)),

    mastery_score NUMERIC(5,2) NOT NULL DEFAULT 0
        CHECK (mastery_score >= 0 AND mastery_score <= 100),

    transfer_score NUMERIC(5,2)
        CHECK (transfer_score IS NULL OR
               (transfer_score >= 0 AND transfer_score <= 100)),

    retention_score NUMERIC(5,2)
        CHECK (retention_score IS NULL OR
               (retention_score >= 0 AND retention_score <= 100)),

    confidence_score NUMERIC(5,2)
        CHECK (confidence_score IS NULL OR
               (confidence_score >= 0 AND confidence_score <= 100)),

    attempts_count INTEGER NOT NULL DEFAULT 0 CHECK (attempts_count >= 0),
    correct_count INTEGER NOT NULL DEFAULT 0 CHECK (correct_count >= 0),
    hint_count INTEGER NOT NULL DEFAULT 0 CHECK (hint_count >= 0),
    feedback_count INTEGER NOT NULL DEFAULT 0 CHECK (feedback_count >= 0),

    self_explanation_count INTEGER NOT NULL DEFAULT 0
        CHECK (self_explanation_count >= 0),

    recovery_count INTEGER NOT NULL DEFAULT 0 CHECK (recovery_count >= 0),
    retrieval_count INTEGER NOT NULL DEFAULT 0 CHECK (retrieval_count >= 0),

    transfer_attempt_count INTEGER NOT NULL DEFAULT 0
        CHECK (transfer_attempt_count >= 0),

    transfer_success_count INTEGER NOT NULL DEFAULT 0
        CHECK (transfer_success_count >= 0),

    time_on_task_seconds DOUBLE PRECISION NOT NULL DEFAULT 0
        CHECK (time_on_task_seconds >= 0),

    mastery_velocity DOUBLE PRECISION,
    hint_dependency_index DOUBLE PRECISION,
    error_persistence_index DOUBLE PRECISION,
    confidence_calibration_error DOUBLE PRECISION,

    first_activity_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ,
    next_review_at TIMESTAMPTZ,
    calculated_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, plan_topic_id, methodology_id)
);

CREATE INDEX idx_stm_user_topic
    ON student_topic_mastery(user_id, plan_topic_id);

CREATE INDEX idx_stm_next_review
    ON student_topic_mastery(next_review_at);

CREATE INDEX idx_stm_intervention
    ON student_topic_mastery(intervention_id);

COMMENT ON TABLE student_topic_mastery IS
    'Current MBADA mastery state and derived learning indicators by student and canonical topic.';


CREATE TABLE research_model_predictions (
    id BIGSERIAL PRIMARY KEY,

    protocol_id BIGINT NOT NULL REFERENCES research_protocols(id) ON DELETE RESTRICT,
    intervention_id BIGINT REFERENCES research_interventions(id) ON DELETE SET NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plan_topic_id INTEGER REFERENCES plan_topics(id) ON DELETE SET NULL,

    prediction_target TEXT NOT NULL,
    prediction_horizon TEXT,

    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,

    predicted_value DOUBLE PRECISION,

    predicted_probability DOUBLE PRECISION
        CHECK (predicted_probability IS NULL OR
               (predicted_probability >= 0 AND predicted_probability <= 1)),

    uncertainty_lower DOUBLE PRECISION,
    uncertainty_upper DOUBLE PRECISION,
    uncertainty_method TEXT,

    calibration_version TEXT,

    feature_snapshot_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    explanation_json JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rmp_protocol_target
    ON research_model_predictions(protocol_id, prediction_target);

CREATE INDEX idx_rmp_user_time
    ON research_model_predictions(user_id, created_at);

CREATE INDEX idx_rmp_topic
    ON research_model_predictions(plan_topic_id);

COMMENT ON TABLE research_model_predictions IS
    'Versioned predictive outputs with uncertainty and calibration metadata; never treated as causal ground truth.';
