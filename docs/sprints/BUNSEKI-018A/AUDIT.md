# BUNSEKI-018A.1 — Auditoría

Fecha: 2026-08-23. Alcance: inspección estática y consultas agregadas de solo lectura a la base SQLite local. No se consultó ni modificó Supabase/PostgreSQL.

## Evidencia de entorno

- Repositorio: `C:/Users/HP/Documents/BunsekiChat`; rama `main`; HEAD inicial `7a674fddc1a3c443117f84b21048e9730e6ca16e`.
- Windows 10, Python 3.13.13, Streamlit 1.57.0; dependencias en `requirements.txt` mediante `pip`.
- El árbol inicial tenía cinco archivos sin seguimiento: `PROMPT.txt`, `app111.py`, `app33.py`, `app34.py` y `app_backup.py`. No fueron alterados.
- No hay suite de tests ni configuración de lint, tipos o formato en archivos rastreados. `pytest --collect-only -q` encontró cero pruebas.

## Arquitectura actual

`app.py` es una aplicación Streamlit monolítica: interfaz, autenticación, acceso a datos, esquema PostgreSQL, analítica, GPS, planes y generación IA conviven en el mismo módulo. Usa `psycopg2` contra `DATABASE_URL` desde secrets o `.env`, Google Gemini mediante `google-genai`, y `st.session_state` para sesión/UI. Los módulos auxiliares son `cohort_management.py`, `research_analytics.py` y `research_engine.py`.

Las tablas PostgreSQL declaradas en `init_db()` son: `users`, `profiles`, `interactions`, `location_events`, `quizzes`, `analytic_plans`, `plan_topics`, `adaptive_quizzes`, `adaptive_questions`, tablas `research_*`, `settings`, `research_cohorts` y trazas de matrícula masiva.

La SQLite local contiene 6 usuarios, 5 perfiles, 60 interacciones, 14 eventos de ubicación y 2 quizzes. Es un esquema legado: sus perfiles no tienen `subject`, `parallel`, `cohort`, identificadores académicos ni tablas de matrícula. Por tanto no representa de forma comprobable el esquema PostgreSQL de producción.

## Hallazgos priorizados

1. **Crítico — aislamiento docente ausente.** `get_teacher_tables()` lee todos los usuarios, interacciones y evaluaciones; `admin_page()` se usa tanto para `admin` como para `teacher` sin filtrar por un docente propietario. Un docente puede acceder a datos ajenos.
2. **Alto — modelo académico desnormalizado.** `profiles` guarda `subject`, `course_level`, `parallel`, `shift`, `cohort` y `teacher` como texto. No existen `Subject`, `AcademicPeriod`, `Parallel`, `Cohort` ni `Enrollment` relacionales.
3. **Alto — ingreso estudiantil todavía editable.** La ficha inicial permite modificar materia, paralelo, jornada y docente. Esto contradice el requisito de asignación exclusiva por matrícula.
4. **Alto — importación no es todo-o-nada.** `import_bulk_enrollment()` confirma filas válidas y registra/rechaza filas inválidas mediante savepoints. Es trazable, pero una carga con errores produce altas parciales; no satisface atomicidad por archivo.
5. **Alto — plan analítico no acepta XLSX.** El uploader admite `txt`, `md`, `docx`, `pdf`; no incluye `xlsx`. El extractor tampoco interpreta libros Excel. Para PDF escaneados, la extracción de texto puede devolver vacío y se depende de `pypdf`/`PyPDF2` opcional.
6. **Medio — datos sensibles.** GPS exacto se almacena por interacción y se muestra/exporta con seis decimales en el panel docente. No hay evidencia de minimización, retención, seudonimización o autorización específica por rol.
7. **Medio — credenciales iniciales configurables con valores inseguros.** El código tiene valores por defecto para el administrador; producción debe depender de secrets seguros y no de defaults.
8. **Medio — preguntas parcialmente contextualizadas.** Gemini recibe historial, temas y plan, pero las entidades pedagógicas son texto. Existe banco local de Cálculo Diferencial y fallback genérico; no hay relaciones de prerrequisitos ni registro de dominio por habilidad.

## Paralelos y gráficos

Las normalizaciones convierten variantes de texto, pero `academic_selectbox()` permite el valor “Otro”; la ficha de estudiante y planes pueden persistir texto libre. Los gráficos filtran/colorean por columnas textuales (`course`, `parallel`, `cohort`) y no por IDs. No fue posible medir variantes reales de paralelo en producción sin abrir la conexión de Supabase.

## GPS

El navegador solicita geolocalización con `streamlit-js-eval`; las coordenadas, precisión y origen se guardan en `interactions` y `location_events`, vinculados por `user_id`. El comportamiento no fue modificado. La UI construye mapa de calor y puntos individuales con coordenadas exactas.

## Resultado de auditoría

No se aplicó una migración de datos. Antes de BUNSEKI-018A.2 se requiere un inventario de solo lectura del esquema PostgreSQL, conteos y valores académicos ambiguos, ejecutado por un responsable autorizado en Supabase.
