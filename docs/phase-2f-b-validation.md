# Fase 2F-B: vista de práctica adaptativa

La navegación estudiantil incorpora **🎯 Práctica adaptativa** para los perfiles
que ya podían usar el tutor y la práctica. La ruta invoca el controlador existente
en el área principal y retorna antes de generar exportaciones o el chat. El tutor
ocupa el ancho disponible y deja de renderizar la práctica. El menú alternativo
hereda la opción automáticamente.

Se mantienen las restricciones de pretest obligatorio y del grupo de control.
`Prueba de nivel` conserva su entrada y su comportamiento de tutor previo, pero ya
no incluye la práctica lateral: esa entrada ya compartía el flujo del tutor en
main. No se implementa una prueba de nivel nueva en esta fase.

## Contexto y persistencia

Los seis argumentos se resuelven explícitamente dentro del flujo autenticado de
`student_page`, después de comprobar el perfil y construir el menú permitido:

| Argumento | Uso real en el controlador |
| --- | --- |
| `user` | Identidad del propietario, claves de estado, preguntas, autosave y dominio |
| `prof` | Nivel inicial y rutas MBADA aprobadas |
| `topic`, `subtopic` | Valores iniciales de los selectores; la selección persistida prevalece |
| `page` | Trazabilidad de la revisión mediante `log_location_event` |
| `user_q` | Histograma de consultas al final de la práctica |

No se mueve el controlador a otro módulo. Sus funciones de persistencia tampoco
cambian. `assessment_attempts`, con `source_key=adaptive_practice:active` y filtro
de propietario, conserva el intento y metadatos. Las respuestas se recuperan de
`assessment_attempt_answers` por propietario e intento; las claves incluyen lote
e identidad de pregunta. Los valores durables de los selectores permiten recuperar
widgets eliminados por Streamlit al navegar. El lote se reconstruye mediante el
proveedor existente de preguntas servidas, con usuario, tema, subtema, dificultad
y ronda. No hay migración ni cambios en cálculo de dominio o temporización.

## Validación ejecutada

Base de referencia: `d1a07b31b5ed346fbfe1f1c4edcbc50d32e19364` (`origin/main`).
Checkout aislado en rama `feat/phase-2f-b-adaptive-view`; copia recuperada preservada.

**Streamlit AppTest: tres pruebas aprobadas.** El arnés compila las funciones reales
de navegación, página estudiantil y práctica mediante AST para evitar el arranque
global de la aplicación y sus conexiones externas. Usa la cabecera y estilos
publicados. Sustituye autenticación externa, GPS, exportaciones, interacciones,
proveedor de preguntas y servicios de dominio por servicios ficticios.

1. Menú real, vista dedicada sin chat ni exportaciones, cinco preguntas y ausencia
   de práctica duplicada en las otras cinco entradas. Restricciones reales del
   menú para pretest pendiente y grupo de control.
2. Revisión MBADA repetida con servicios simulados: una llamada de escritura de
   dominio para la ronda. No equivale a validar el dominio en PostgreSQL.
3. Adaptadores reales de intentos/respuestas y PostgreSQL temporal: tres respuestas
   parciales; ida a progreso y regreso; mismo intento, claves, preguntas y valores;
   sustitución completa de AppTest; usuario distinto sin respuestas cruzadas;
   revisión repetida sin duplicar intentos ni respuestas; siguiente ronda con otro
   lote y sin respuestas heredadas; recuperación de ronda y dificultad en nueva
   sesión. Cambio a Geometría y modo manual Intermedio, navegación al tutor y
   recuperación de la misma selección y lote en una nueva sesión.

Antes de escribir se verificaron host `127.0.0.1`, puerto externo `55440`, base
`bunseki_release_qa` y marcador `release_qa_marker=bunseki-release-20261018`.
PostgreSQL informó versión 17.11 y puerto interno 5432. Docker CLI no estaba
disponible, por lo que no se inspeccionó el contenedor por su nombre. Solo se
recrearon datos de los usuarios ficticios reservados 8261/8262; no se truncaron
tablas. El usuario 8263 se reservó para la vista previa local.

Reproducción desde la raíz, con las dependencias reales instaladas:

```powershell
# Inyectar BUNSEKI_VIEW_QA_DSN por un mecanismo local; nunca guardarlo en Git.
python -m unittest discover -s tests -p test_student_practice_view.py -v
```

Sin la variable, se ejecutan las dos pruebas simuladas y se omite la de PostgreSQL.
La prueba de PostgreSQL exige la identidad y el marcador de la base temporal antes
de modificar sus usuarios ficticios. No apunta a Supabase ni a bunseki_test.

## Limitaciones y revisión pendiente

No se ejecutó un recorrido de la aplicación en navegador real: el navegador de
herramientas no pudo acceder a los servidores locales. La vista previa HTML es
estática, ilustrativa y usa preguntas ficticias extraídas del arnés AppTest; no
guarda respuestas. No se verificó visualmente en navegador.

No se reinició PostgreSQL ni Streamlit y no se completó el formulario real de
login/logout. La sustitución de AppTest verifica recuperación desde PostgreSQL,
no esos recorridos. Las preguntas son deterministas y simuladas: no se comprobó
en esta fase la recuperación del proveedor real de `ai_practice_question_serves`.
Pretest, posttest y evaluaciones docentes no se rindieron de extremo a extremo;
sus controladores permanecen sin cambios. No se midieron umbrales de rendimiento;
se conserva el código existente de temporización.

La comparación AST contra main confirma que solo cambian `student_page` y
`render_student_sidebar`; los otros 265 cuerpos de funciones permanecen idénticos.
`git diff --check` pasó.

No se publica ni se integra en main con esta entrega.
