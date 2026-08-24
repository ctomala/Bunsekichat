# Modelo académico objetivo

```text
users ── 0..1 teachers
users ── 0..1 students
teachers ──< teacher_subjects >── subjects
academic_periods ──< courses >── subjects
courses ──< parallels ──< cohorts
students ──< enrollments >── cohorts
curricula ──< curriculum_versions ──< units ──< topics ──< subtopics
topics/subtopics ──< learning_outcomes ──< skills
skills/topics/subjects ──< prerequisite relations
```

`Enrollment` es histórico e inmutable en su alcance académico: `student_id`, `cohort_id`, `status`, `research_group`, fechas y metadatos de importación. Una persona puede tener varias matrículas. `Course` representa período + materia; `Parallel` pertenece a un curso; `Cohort` pertenece a un paralelo.

La materia inicial “Álgebra Elemental / Precálculo” debe ser un registro en `subjects`, no una constante de negocio. Su currículo y las 14 unidades propuestas se modelarán como `curriculum_version`, `unit`, `topic` y `skill`, publicables solo tras revisión docente.

Para investigación, un data mart o vista separada debe emitir `research_student_id` derivado y estable, IDs académicos, medidas y eventos; debe excluir por defecto nombre, correo, usuario, contraseña, dirección y coordenadas GPS exactas.
