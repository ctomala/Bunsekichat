# BunsekiChat: cohorte oficial y matrícula masiva

## Archivos de despliegue

- `app.py`
- `cohort_management.py`
- `supabase_cohort_enrollment_update.sql`
- `verify_supabase_cohort_setup.sql`
- `requirements.txt`

## Aplicación de la migración

1. Abrir Supabase y seleccionar el proyecto de BunsekiChat.
2. Entrar en **SQL Editor** y crear una consulta nueva.
3. Ejecutar `supabase_cohort_enrollment_update.sql` completo.
4. Ejecutar `verify_supabase_cohort_setup.sql`.
5. Confirmar que existe `COHORTE_INVESTIGACION_CALCULOI_2026` y que las consultas de duplicados no devuelven filas.

La migración no elimina tablas ni registros. Los datos históricos quedan como `piloto` y con `usar_en_investigacion=false`.

## Matrícula masiva

1. Ingresar como docente o administrador.
2. Abrir **Matrícula masiva**.
3. Descargar la plantilla Excel.
4. Completar cédula, nombres, apellidos, correo, materia, curso, paralelo, jornada y grupo.
5. Subir el archivo y revisar la validación.
6. Crear los estudiantes válidos.
7. Descargar las credenciales del lote y entregarlas individualmente.

Las contraseñas temporales se muestran una sola vez. La base almacena únicamente el hash y el indicador `password_temporal`.

## Primer ingreso

El estudiante debe confirmar sus datos, aceptar el consentimiento y cambiar la contraseña. Solo entonces se activa `usar_en_investigacion=true` y se habilita el pretest.

## Análisis principal

El panel de investigación abre por defecto con esta condición:

```text
estado_dato = oficial
usar_en_investigacion = true
consentimiento_informado = true
```

Las vistas piloto y de auditoría son opcionales y quedan identificadas como no pertenecientes al análisis principal.
