# BunsekiChat UI UX 02.3 y Fase 2F-A

Esta actualización incorpora los cambios locales acumulados de presentación de inicio, acceso, administración, docente y estudiante. La práctica adaptativa se extrae a render_student_adaptive_practice dentro de app.py y conserva su llamada en la misma columna y sus seis parámetros.

## Alcance

Se publica el app.py recuperado, los doce archivos de bunseki/ui y el logo necesario para la interfaz. No se incluyen parches auxiliares, respaldos locales ni archivos de configuración privados. No hay cambios en migraciones, requisitos ni servicios de persistencia.

SHA-256 de app.py: 414951733e00f71868b19f4fc2b10aad504888ff684f6c6caf1de66b4805f4e2. Coincide con la certificación original de Fase 2F-A.

## Validación del 18 de octubre de 2026

- 31 pruebas de regresión aprobadas.
- 68 comprobaciones aisladas aprobadas: equivalencia estructural, claves de widgets, callbacks, respuestas simuladas, navegación y componentes de presentación.
- El arnés conserva como registro un fallo histórico ya corregido del propio arnés; no se observa un fallo actual de la aplicación en estas comprobaciones.
- El inventario de la copia recuperada difiere del original por la exclusión de descargas y otros archivos ajenos al despliegue. app.py y los doce archivos UI conservan los hashes certificados.
- 25 comprobaciones reales de persistencia aprobadas en PostgreSQL 17.11 desechable en localhost:55440: creación y recuperación de intento, autosave de cinco respuestas, aislamiento por usuario, reentrada, conservación de metadatos, tiempo transcurrido, rollback, idempotencia y rechazo de respuestas tardías.
- 18 comprobaciones adicionales aprobadas con Streamlit AppTest y PostgreSQL real, comparando antes y después de la extracción. Tres respuestas sobreviven al reemplazo completo de sesión y conservan el mismo ID de intento, sin duplicaciones.
- El proveedor de preguntas de las pruebas usa ítems ficticios; el guardado, recuperación y callbacks emplean las funciones originales y los servicios reales.
- Límites: no se probaron reinicio físico del navegador o servidor, política completa de expiración, generación externa de IA ni un recorrido completo autenticado Gold/pretest/posttest en producción. Los componentes de persistencia y temporizador no se modifican en esta actualización.

## Estado de publicación

Pruebas previas aprobadas para integrar esta actualización de presentación y extracción equivalente. La comprobación online debe realizarse después de integrar en main; este informe no certifica todavía el despliegue ni todo el recorrido académico en producción.
