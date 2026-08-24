# Plan de migración reversible y no destructivo

## Precondiciones bloqueantes

1. Backup verificado y consulta de solo lectura al esquema PostgreSQL/Supabase.
2. Inventario agregado de `profiles.subject`, `course_level`, `parallel`, `shift`, `cohort`, `teacher` y duplicados de identidad, sin exportar PII.
3. Decisión del Founder sobre el mapeo de valores ambiguos; los ambiguos no se migran automáticamente.

## Fases

1. Agregar tablas normalizadas y catálogos, sin modificar ni borrar columnas históricas.
2. Crear `students`/`teachers` y vincularlos a `users`; crear `academic_periods`, `subjects`, `courses`, `parallels`, `cohorts` y `enrollments` con claves foráneas e índices.
3. Sembrar solo catálogos aprobados, incluido “Álgebra Elemental / Precálculo”. No codificar la lista en la UI.
4. Crear una tabla de candidatos de migración y un reporte: migrado, ambiguo, omitido, error. Solo registros inequívocos reciben matrícula histórica; el histórico permanece intacto.
5. Cambiar las altas nuevas a una transacción atómica: validar todo el archivo, previsualizar, insertar estudiante/matrícula/credenciales o realizar rollback completo.
6. Introducir consultas por alcance docente y pruebas de aislamiento antes de mostrar filtros o exportaciones a un rol `TEACHER`.
7. Añadir referencias opcionales a IDs en eventos y analítica; conservar las columnas de texto para compatibilidad durante una ventana de migración explícita.

## Rollback

Cada migración debe tener script de reversión limitado a tablas/campos nuevos sin borrar información histórica. Las migraciones de datos deben registrar su lote y permitir desasociar vínculos creados por el lote, nunca eliminar usuarios, perfiles, interacciones, GPS ni evaluaciones.
