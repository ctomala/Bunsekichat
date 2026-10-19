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
- Pendientes: continuidad real de intentos persistidos, autosave, temporizadores y comprobación de navegador con PostgreSQL aislado. Los cuatro grupos pendientes del informe original siguen pendientes.

## Estado de publicación

Propuesta preparada para revisión. No representa todavía un despliegue verificado ni una certificación completa de continuidad. Completar la validación pendiente antes de integrar en main y comprobar la aplicación en Streamlit después del despliegue.
