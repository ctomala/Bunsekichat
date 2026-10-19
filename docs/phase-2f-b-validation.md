# Fase 2F-B: validación final del PR #3

La práctica adaptativa tiene una entrada propia en el menú estudiantil y se
renderiza en el área principal, sin duplicarse en el tutor. El controlador sigue
en app.py y recibe explícitamente usuario, perfil, tema, subtema, página y consultas.
Se conserva la navegación existente y el diseño publicado.

## Cambio adicional encontrado durante el recorrido

**FAIL inicial, corregido y repetido con PASS:** al contraer el panel lateral,
no se podía reabrir para llegar a Cerrar sesión. El CSS heredado ocultaba stToolbar,
el padre del botón moderno stExpandSidebarButton. Además, el selector antiguo
trataba stSidebarCollapseButton como un botón, cuando en esta versión es un div,
y dejaba el control de contraer oculto fuera del hover.

La corrección en bunseki/ui/student_dashboard.py está limitada a páginas con
.bui-student-surface: muestra la barra cuando contiene el botón de reapertura,
conserva ocultos Deploy/menú/acciones del framework y hace visible el control de
contraer. Se verificó contraer y reabrir en escritorio (1365×900) y ventana estrecha
(714 px), sin manipular estado de React ni ejecutar JS que cambie el DOM.
No se cambió ningún controlador de autenticación, persistencia, evaluación o dominio.

## Aislamiento

Se verificó PostgreSQL 17.11 en 127.0.0.1:55440, base bunseki_release_qa y marcador
bunseki-release-20261018. Como su esquema anterior era mínimo, se creó una base
separada, bunseki_browser_qa_2fb, con marcador bunseki-browser-qa-2fb, dentro del
mismo servidor temporal. No se usaron Supabase, bunseki_test ni bases recuperadas.
El cliente Docker se encontró, pero el acceso a su pipe fue denegado: se certificó
el servidor y sus marcadores, no el nombre del contenedor.

El arnés tests/qa_student_practice_browser_app.py ejecuta la aplicación completa,
incluido el formulario real de login. Impide cargar dotenv y secretos del usuario,
valida host/puerto/base/marcador antes de escribir y rechaza destinos alternativos,
incluidas sobrescrituras por database o hostaddr. Las contraseñas se inyectan por
variables locales y no se guardan en Git. Los estudiantes 1/2 pertenecen al navegador;
los estudiantes 3/4 se reservan para la prueba automatizada.

Las preguntas son sumas ficticias deterministas sembradas en el banco local.
Se ejecutaron las funciones reales de asignación de ai_practice_question_serves,
autosave y revisión del banco. La generación/verificación por IA externa se
deshabilitó: **SKIP intencionado**, no se declara probada. La denominación Matrices
solo ejercita selección/persistencia y no acredita calidad pedagógica de las sumas.

## Navegador real

Se usó Chromium del navegador integrado contra http://127.0.0.1:8531. El intento
inicial con control nativo de Chrome fue detenido por la herramienta al no poder
identificar su URL. Los posteriores timeouts de revisión automática interrumpieron
algunas acciones; se continuó con autorización del usuario y se completaron los
pasos pendientes. Esos timeouts no se contabilizan como recorridos ejecutados.

| Paso solicitado | Resultado | Evidencia |
| --- | --- | --- |
| 1. Login de estudiante ficticio | PASS | Formulario real, Estudiante QA 1 |
| 2. Vista propia y ausencia de duplicación en tutor | PASS | Tutor sin el encabezado/controlador de práctica; capturas 01 y 04 |
| 3. Elegir tema/subtema/dificultad y responder parcialmente | PASS | Álgebra lineal / Matrices / Intermedio; respuestas 57, 31, 24 |
| 4. Registrar identidad, lote, preguntas, respuestas y ronda | PASS | Intento 4, ronda 1, cinco preguntas; JSON de UI y PostgreSQL |
| 5–6. Tutor, progreso y regreso con el mismo intento | PASS | Comparación exacta de preguntas/opciones/selecciones y snapshot PostgreSQL |
| 7. Recarga y recuperación | PASS | La recarga vuelve al acceso; tras login se recupera el mismo progreso |
| 8. Logout/login del mismo estudiante | PASS | Cierre real y reingreso en la misma pestaña, misma selección y respuestas |
| 9. Segundo estudiante y bloqueo de acceso ajeno | PASS | Estudiante QA 2 sin respuestas heredadas; servicios rechazan load/save/resume/submit del intento 4 con otro propietario |
| 10. Reinicio real de Streamlit y recuperación | PASS | PID 23460 → 23708; luego 13272 y 10132 al verificar la corrección final; recuperación visual y PostgreSQL |
| 11. Revisar y avanzar sin duplicar/perder estados | PASS | Revisión 4/5 repetida mantiene cinco registros; ronda 2 cambia lote y conserva Intermedio, sin respuestas heredadas |
| Recuperar ronda 2 tras otro reinicio | PASS | Mismas cinco preguntas de ronda 2, modo manual y ninguna respuesta seleccionada |
| Contraer/reabrir panel y acceder al logout | PASS | Regresión visual repetida después de corregir el CSS, incluidas ventanas estrechas |

Recargar o reiniciar exige volver a iniciar sesión: la autenticación existente
vive en la sesión de Streamlit. La práctica se recupera desde PostgreSQL después
de autenticarse. No se añadió autenticación persistente mediante cookies.

## Evidencia de persistencia

```text
propietario ficticio: 2; otro estudiante ficticio: 3
attempt_id: 4; assessment_kind: practice; status: in_progress
ronda inicial: 1; ronda final: 2
modo/dificultad: Intermedio / Intermedio
lote 1: f42fb2bd66f52b311301db8aa7b4c9c622e300e5ec7b5ebfc00f57393f8abf15
lote 2: 1442f34b501ab98e305fc97097b8f03be62124306b12adcce5b3e35ddd47969b
preguntas iniciales: QA ficticia 19, 10, 8, 16, 9
respuestas parciales: 57, 31, 24, sin responder, sin responder
resultado revisado: 4/5
intentos antes/después: 1 / 1
respuestas tras completar/revisar/revisar/avanzar: 5 / 5 / 5 / 5
registros del banco tras revisar/revisar: 5 / 5
preguntas servidas por lote: 5; lotes sin IDs de pregunta compartidos
```

Las cinco respuestas de la ronda anterior permanecen guardadas al avanzar. Sus
claves incluyen el lote y no se aplican a las preguntas nuevas. Las comparaciones
exactas entre snapshots antes y después de navegación/reingreso/reinicio pasaron.
El resumen portable está en docs/evidence/phase-2f-b/resultados.json.

## Temporizadores que sí corresponden

La práctica no configura un límite ni cuenta atrás de expiración: expires_at
permanece NULL. El autosave existente envía elapsed_seconds=0, y las cinco filas
persistidas conservan cero. started_at permanece estable; last_activity_at y
updated_at se actualizan con la actividad. No se inventó ni añadió expiración.

session_guard aplica el timeout general configurado en settings (20 minutos por
defecto). Se inspeccionó el contrato, pero **SKIP** de una espera real de 20 minutos.
Los logs reales de revisión conservaron MBADA_REVIEW_TIMING; las dos revisiones
observadas fueron 0.053 y 0.067 segundos en este entorno ficticio, sin certificar
un umbral de rendimiento ni extrapolarlo a producción o a IA externa.

## Pruebas automatizadas: seis PASS

Última ejecución: seis pruebas, cero fallos, 73.574 segundos.

- Tres pruebas originales de test_student_practice_view.py: navegación/permisos,
  idempotencia de dominio con servicios simulados y continuidad con PostgreSQL.
- Una prueba de test_student_practice_full_app.py: aplicación completa, login real,
  banco servido en PostgreSQL, navegación, logout, cliente nuevo, aislamiento,
  revisión repetida, tiempos cero y siguiente ronda. Incluye rechazo de las cuatro
  operaciones ajenas contra el servicio real.
- Dos pruebas de test_student_practice_qa_isolation.py: destino local permitido y
  rechazo de sobrescrituras externas o de la base recuperada, sin hacer conexiones.

AppTest conserva un delta de checkbox después de session_state.clear(). El arnés
usa un cliente nuevo tras ejecutar el logout real; no presenta eso como un logout/
login en la misma pestaña. Ese recorrido sí se ejecutó separadamente en navegador.

Reproducción desde la raíz del checkout, inyectando localmente las variables
BUNSEKI_VIEW_QA_DSN, BUNSEKI_BROWSER_QA_DSN y BUNSEKI_BROWSER_QA_PASSWORD:

```powershell
python -m unittest discover -s tests -p "test_student_practice*.py" -v
python -m streamlit run tests/qa_student_practice_browser_app.py --server.address 127.0.0.1 --server.port 8531
```

Las pruebas de integración se omiten sin sus DSN. El arnés de navegador exige
su base y marcador exactos, y crea el esquema y las preguntas ficticias sin borrar
los datos de los estudiantes del recorrido manual. El supervisor solo permite
reiniciar/detener ese proceso local; no ejecuta comandos arbitrarios del archivo.

## Capturas y límites reales

Se guardaron doce capturas de viewport, sin pantallas de credenciales ni datos
personales de estudiantes reales. Seis se incluyen en docs/evidence/phase-2f-b;
el conjunto local está en outputs/capturas-2f-b. Las capturas de Streamlit muestran
el área visible de su contenedor desplazable, no toda la página en una sola imagen.

**SKIP:** servicio IA externo; cálculo de dominio MBADA con una ruta aprobada real
en PostgreSQL (la práctica libre no tenía esa ruta; la idempotencia se cubre con
servicios simulados); rendir de extremo a extremo pretest, posttest o evaluación
docente; reiniciar PostgreSQL; auditoría exhaustiva de dispositivos/accesibilidad.
No se tocaron sus controladores, ni se cambiaron permisos de usuarios o contratos
de persistencia. La verificación estrecha se limita a reapertura y uso del panel.

La rama continúa sobre el PR #3 y el checkout recuperado permanece intacto. La
validación técnica está completada para este alcance. El estado de publicación
y revisión debe comprobarse en el PR existente. No integrar en main ni desplegar
en Streamlit en esta fase.
