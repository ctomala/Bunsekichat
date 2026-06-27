-- =========================================================
-- BUNSEKICHAT - COHORTES Y MATRICULA MASIVA
-- Migracion no destructiva e idempotente para Supabase.
-- Los registros previos se conservan y se clasifican como piloto.
-- =========================================================

BEGIN;

CREATE TABLE IF NOT EXISTS research_cohorts(
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    research_title TEXT NOT NULL,
    subject TEXT,
    course_level TEXT,
    academic_year INTEGER,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TEXT NOT NULL
);

INSERT INTO research_cohorts(
    code, name, research_title, subject, course_level, academic_year, active, created_at
)
VALUES(
    'COHORTE_INVESTIGACION_CALCULOI_2026',
    'Cohorte oficial Cálculo I 2026',
    'Efectos de un Tutor Inteligente basado en Inteligencia Artificial Generativa sobre el Rendimiento Académico en Cálculo Diferencial en la Universidad de Guayaquil',
    'Cálculo I',
    '1',
    2026,
    TRUE,
    CURRENT_TIMESTAMP::TEXT
)
ON CONFLICT (code) DO UPDATE SET
    name=EXCLUDED.name,
    research_title=EXCLUDED.research_title,
    subject=EXCLUDED.subject,
    course_level=EXCLUDED.course_level,
    academic_year=EXCLUDED.academic_year,
    active=TRUE;

ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS password_temporal BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS primer_ingreso BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS cedula TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS correo TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS estado_dato TEXT NOT NULL DEFAULT 'piloto';
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS usar_en_investigacion BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS consentimiento_informado BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS fecha_consentimiento TEXT;
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS pretest_estado TEXT NOT NULL DEFAULT 'pendiente';
ALTER TABLE IF EXISTS profiles ADD COLUMN IF NOT EXISTS posttest_estado TEXT NOT NULL DEFAULT 'pendiente';

-- Proteccion explícita para datos históricos. No modifica registros oficiales.
UPDATE profiles
SET estado_dato='piloto', usar_en_investigacion=FALSE
WHERE estado_dato IS NULL OR BTRIM(estado_dato)='';

UPDATE profiles p
SET pretest_estado='completado'
WHERE EXISTS (
    SELECT 1 FROM adaptive_quizzes aq
    WHERE aq.user_id=p.user_id AND aq.quiz_type='pretest' AND aq.status='completed'
);

UPDATE profiles p
SET posttest_estado='completado'
WHERE EXISTS (
    SELECT 1 FROM adaptive_quizzes aq
    WHERE aq.user_id=p.user_id AND aq.quiz_type='posttest' AND aq.status='completed'
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_profiles_cedula
    ON profiles(cedula)
    WHERE cedula IS NOT NULL AND BTRIM(cedula)<>'';

CREATE UNIQUE INDEX IF NOT EXISTS uq_profiles_correo_lower
    ON profiles(LOWER(correo))
    WHERE correo IS NOT NULL AND BTRIM(correo)<>'';

CREATE INDEX IF NOT EXISTS idx_profiles_research_scope
    ON profiles(estado_dato, usar_en_investigacion, consentimiento_informado, cohort, research_group);

CREATE TABLE IF NOT EXISTS bulk_enrollment_batches(
    id SERIAL PRIMARY KEY,
    cohort_code TEXT REFERENCES research_cohorts(code) ON DELETE RESTRICT,
    source_filename TEXT,
    imported_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    total_rows INTEGER NOT NULL DEFAULT 0,
    created_rows INTEGER NOT NULL DEFAULT 0,
    rejected_rows INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bulk_enrollment_rows(
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES bulk_enrollment_batches(id) ON DELETE CASCADE,
    source_row INTEGER,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    cedula TEXT,
    correo TEXT,
    status TEXT NOT NULL,
    detail TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bulk_enrollment_rows_batch
    ON bulk_enrollment_rows(batch_id, status);

-- Vista de compatibilidad con los nombres solicitados por el protocolo.
CREATE OR REPLACE VIEW research_student_registry AS
SELECT
    u.id AS user_id,
    p.cedula,
    p.first_names AS nombres,
    p.last_names AS apellidos,
    p.correo,
    p.subject AS materia,
    p.course_level AS curso,
    p.parallel AS paralelo,
    p.shift AS jornada,
    p.research_group AS grupo_investigacion,
    p.cohort AS cohorte,
    p.estado_dato,
    p.usar_en_investigacion,
    p.consentimiento_informado,
    p.fecha_consentimiento,
    p.pretest_estado,
    p.posttest_estado,
    u.password_temporal,
    u.primer_ingreso,
    u.active,
    u.created_at
FROM users u
JOIN profiles p ON p.user_id=u.id
WHERE LOWER(COALESCE(u.role, 'student'))='student';

COMMIT;
