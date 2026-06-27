-- Verificación de la migración de cohortes. Solo realiza lecturas.

SELECT code, name, subject, course_level, academic_year, active
FROM research_cohorts
WHERE code='COHORTE_INVESTIGACION_CALCULOI_2026';

SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema='public'
  AND (
      (table_name='profiles' AND column_name IN (
          'cedula','correo','estado_dato','usar_en_investigacion','consentimiento_informado',
          'fecha_consentimiento','pretest_estado','posttest_estado','cohort','research_group'
      ))
      OR (table_name='users' AND column_name IN ('password_temporal','primer_ingreso'))
  )
ORDER BY table_name, column_name;

SELECT
    COALESCE(estado_dato, 'piloto') AS estado_dato,
    COUNT(*) AS estudiantes,
    COUNT(*) FILTER (WHERE usar_en_investigacion) AS autorizados_analisis,
    COUNT(*) FILTER (WHERE consentimiento_informado) AS con_consentimiento
FROM profiles
GROUP BY COALESCE(estado_dato, 'piloto')
ORDER BY estado_dato;

SELECT cedula, COUNT(*) AS repeticiones
FROM profiles
WHERE cedula IS NOT NULL AND BTRIM(cedula)<>''
GROUP BY cedula
HAVING COUNT(*)>1;

SELECT LOWER(correo) AS correo, COUNT(*) AS repeticiones
FROM profiles
WHERE correo IS NOT NULL AND BTRIM(correo)<>''
GROUP BY LOWER(correo)
HAVING COUNT(*)>1;

SELECT
    COUNT(*) AS estudiantes_oficiales_incluidos
FROM research_student_registry
WHERE estado_dato='oficial'
  AND usar_en_investigacion=TRUE
  AND consentimiento_informado=TRUE
  AND cohorte='COHORTE_INVESTIGACION_CALCULOI_2026';

