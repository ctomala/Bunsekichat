# BunsekiChat R8.22 - Metodologia + Investigacion

## Metodologia

Nombre de trabajo:
Metodologia Bunseki de Aprendizaje por Dominio Adaptativo (MBADA v1.0).

Ciclo del estudiante:

DIAGNOSTICA -> EXPLORA -> COMPRENDE -> EXPLICA -> PRACTICA -> ASCIENDE -> DEMUESTRA -> RECUPERA -> REFLEXIONA

El curriculo oficial permanece en plan_topics.
La metodologia se almacena separadamente y requiere revision/aprobacion docente.

## Principios

- Dominio antes de progresion.
- Andamiaje decreciente.
- Ejemplo trabajado cuando el conocimiento previo es insuficiente.
- Preguntas socraticas y autoexplicacion.
- Practica adaptativa.
- Transferencia a problemas nuevos.
- Recuperacion dirigida por error.
- Recuperacion espaciada.
- Metacognicion y reflexion.
- Docente en control de la aprobacion.

## Investigacion

Secuencia:

Consentimiento -> Grupo -> Pretest -> Intervencion -> Posttest -> Encuesta/Analitica

El pretest y posttest son instrumentos de medicion.
No deben incluir pistas, tutorias ni retroalimentacion de la intervencion.

El posttest debe permanecer bloqueado mientras la intervencion requerida no haya terminado.

## Integridad causal

Registrar siempre:

- grupo asignado
- baseline/pretest
- protocolo y version
- metodologia y version
- inicio y fin de intervencion
- exposicion o dosis
- secuencia temporal
- adherencia
- contaminacion
- desviaciones del protocolo
- outcome/posttest
- conjunto de ajuste
- DAG causal
- plan de analisis

Correlacion no equivale a causalidad.
Los estimadores causales solo deben interpretarse bajo los supuestos documentados.

## Indicadores de aprendizaje

- mastery_score
- diagnostic_score
- mastery_velocity
- transfer_score
- retention_score
- hint_dependency_index
- error_persistence_index
- confidence_calibration_error
- time_on_task_seconds
- attempts_count
- correct_count
- recovery_count
- retrieval_count
- self_explanation_count
- transfer_success_count

## Indicadores de investigacion

- score_pretest
- score_posttest
- ganancia_absoluta
- ganancia_normalizada
- efecto por grupo
- dosis de intervencion
- adherencia
- exposicion por tema
- contaminacion
- desviacion del protocolo
- version metodologica recibida

## Analitica predictiva

Las predicciones deben almacenar:

- variable objetivo
- horizonte
- modelo
- version
- valor o probabilidad
- intervalo/incertidumbre
- metodo de incertidumbre
- version de calibracion
- snapshot de variables de entrada

Se evaluaran posteriormente:

- MAE / RMSE para puntajes
- Brier score para probabilidades
- log loss
- calibracion
- discriminacion
- estabilidad temporal
- drift
- validacion fuera de muestra

## Analitica causal futura

El sistema quedara preparado para:

- diferencia ajustada pretest-posttest
- ANCOVA
- ATE
- ATT
- efectos heterogeneos
- modelos doubly robust cuando el diseno y la muestra lo permitan
- analisis de sensibilidad

Los modelos predictivos y causales se mantendran separados.

## Gobierno

Ninguna propuesta generada por IA se convierte automaticamente en metodologia oficial.
El docente revisa, edita y aprueba.

Cada metodologia conserva version y responsable de aprobacion.

Este documento se ampliara durante R8.22C-R8.22G para generar:

1. Guia didactica docente.
2. Guia sencilla para estudiantes.
3. Manual tecnico de analitica e investigacion.


## R8.22C1 - Interfaz Docente MBADA

Se incorpora al gestor docente de planes analiticos una ficha metodologica
versionada para cada plan_topic.

Flujo de gobierno:

BORRADOR -> REVISADO -> APROBADO

Una metodologia aprobada no se sobrescribe. Para modificarla se crea una nueva
version en borrador, preservando la version aplicada para trazabilidad docente
e investigativa.

La ficha MBADA incluye objetivo pedagogico, prerrequisitos, conceptos
esenciales, pregunta guia, las nueve fases DIAGNOSTICA, EXPLORA, COMPRENDE,
EXPLICA, PRACTICA, ASCIENDE, DEMUESTRA, RECUPERA y REFLEXIONA, ejemplo
trabajado, preguntas socraticas, transferencia, umbral de dominio, recuperacion
espaciada y notas docentes.

Antes de pasar a revision, Bunseki exige que los componentes pedagogicos
centrales esten completos. Una version aprobada queda congelada para
trazabilidad metodologica e investigativa.

R8.22C1 corresponde a autoria manual. La generacion de una propuesta
metodologica con IA se incorpora en R8.22D y siempre quedara sujeta a revision
y aprobacion docente.

## R8.22D1 - Generacion de propuesta metodologica

Se incorpora la generacion asistida de una propuesta MBADA para cada tema
curricular. En la interfaz el boton se denomina "Generar propuesta
metodologica"; no utiliza la expresion IA como nombre de la accion.

MBADA significa Metodologia Bunseki de Aprendizaje por Dominio Adaptativo.

La propuesta utiliza el motor Gemini ya configurado en BunsekiChat y toma como
contexto exclusivamente el plan_topic canonico: unidad, tema, subtema,
resultado de aprendizaje, Bloom, palabras clave y evidencia documental
disponible.

Gobierno academico:

- la generacion no modifica plan_topics;
- la generacion no aprueba una metodologia;
- la propuesta se carga primero en la interfaz para revision;
- el docente puede modificar cualquier campo antes de guardar;
- la aprobacion continua separada del proceso de generacion;
- ai_generated, ai_model y prompt_version registran trazabilidad tecnica;
- la procedencia curricular sigue siendo la fuente oficial almacenada en
  plan_topics.

Version inicial del prompt metodologico: R8.22D1-MBADA-1.0.
Modelo inicial: gemini-2.5-flash.

## R8.22D2B - Actualizacion resiliente del proveedor generativo

Se actualiza el generador metodologico MBADA para utilizar modelos Gemini
vigentes y un fallback controlado. La interfaz conserva el nombre
"Generar propuesta metodologica" y no incorpora la expresion IA en el boton.

Orden de modelos para la propuesta metodologica:
1. gemini-3.8-flash
2. gemini-3.6-flash
3. gemini-3.5-flash
4. gemini-3.5-flash-lite

El modelo que realmente completa la propuesta se registra en ai_model. La
version del prompt se actualiza a R8.22D2B-MBADA-1.1. El contenido curricular
oficial continua procediendo exclusivamente de plan_topics y la generacion no
realiza aprobacion automatica.

## R8.22D2D-R - Recuperacion de borrador vacio e hidratacion del formulario

Se detecto un borrador existente creado durante la prueba visual antes de que
los widgets de Streamlit recibieran la propuesta generada. El registro se
conserva para mantener trazabilidad y se reutiliza como la misma version 1.

Este ajuste no crea, elimina ni modifica registros de metodologia durante la
instalacion. Cuando el docente vuelva a generar una propuesta para el mismo
tema, los valores se cargaran en los campos editables del formulario. Si luego
el docente decide guardar, se actualizara el borrador existente en lugar de
crear una nueva version.

La propuesta permanece separada del curriculo oficial y requiere revision
docente antes de cualquier cambio de estado.

## R8.22E1 - Fundamento de dominio del estudiante

Se integra el primer flujo operativo de dominio MBADA en la experiencia de
práctica del estudiante sin reemplazar el motor adaptativo existente.

### Decisiones de diseño

- El estudiante puede activar explícitamente una ruta MBADA aprobada compatible
  con su contexto académico.
- MBADA significa Metodología Bunseki de Aprendizaje por Dominio Adaptativo.
- La ruta usa `plan_topic_id` y `methodology_id`; no modifica `plan_topics`.
- Solo las metodologías con estado `approved` pueden registrar dominio.
- La aprobación de una evaluación y el dominio MBADA son conceptos diferentes.
  El umbral histórico de aprobación de quiz permanece intacto; el dominio usa
  el `mastery_threshold` de la versión metodológica aprobada.
- `student_topic_mastery` mantiene una fila por
  `(user_id, plan_topic_id, methodology_id)`.
- En R8.22E1, `attempts_count` representa preguntas de práctica respondidas,
  `correct_count` aciertos acumulados, `feedback_count` retroalimentaciones
  mostradas y `retrieval_count` rondas de práctica completadas.
- `mastery_score` es, en esta primera implementación, exactitud acumulada en la
  práctica vinculada a la versión metodológica. Es un indicador descriptivo de
  aprendizaje y no un estimador causal.
- `mastery_state` usa los estados ya autorizados por el esquema:
  `not_started`, `developing`, `proficient` y `mastered` en este flujo.
- `error_persistence_index` se calcula descriptivamente como proporción
  acumulada de respuestas incorrectas.
- `mastery_velocity` se calcula desde la segunda ronda como cambio del
  `mastery_score` respecto del valor acumulado anterior.
- R8.22E1 no escribe todavía `research_intervention_events`; la instrumentación
  experimental y causal permanece separada para la fase de protocolo.
- La práctica libre existente continúa disponible y no genera registros MBADA.

### Gobernanza

El docente sigue controlando la metodología. Una versión aprobada queda
congelada; una nueva versión metodológica producirá una nueva trayectoria de
dominio sin reescribir la evidencia obtenida con versiones anteriores.

## R8.22E4 - Adaptatividad pedagógica y deduplicación semántica

R8.22E3 confirmó la persistencia e idempotencia del dominio, pero la prueba visual detectó que una ruta MBADA podía permanecer en nivel manual y que dos ítems diferentes del banco podían representar la misma tarea matemática.

Cuando una ruta MBADA aprobada está activa, la dificultad pasa a modo `Recomendado`. La práctica libre fuera de MBADA conserva la selección manual. El dominio MBADA continúa separado de la regla histórica de aprobación del 70%.

La reserva de preguntas incorpora una firma matemática conservadora para evitar equivalencias dentro de una misma ronda y para no volver a presentar al mismo estudiante una tarea matemáticamente equivalente ya servida. La misma regla se aplica al almacenamiento de nuevos ítems para reducir reformulaciones equivalentes futuras.

R8.22E4 no reescribe resultados históricos de dominio, no altera el currículo y no crea eventos de investigación.

## R8.22E5 - Hotfix de reserva PostgreSQL con RealDictCursor

La prueba de ascenso adaptativo confirmó que MBADA selecciona correctamente el
modo `Recomendado`, pero la creación de la ronda Básico falló antes de servir
preguntas. El proveedor Gemini respondió correctamente y pudo producir JSON
válido, por lo que el origen no era el modelo.

La causa raíz estaba en la función de reserva introducida durante R8.22E4:
la conexión PostgreSQL de BunsekiChat usa `RealDictCursor`, mientras que parte
de la nueva reserva trataba las filas como tuplas mediante índices posicionales
(`row[0]`, `row[1]`) y desempaquetado. En una `RealDictRow`, el acceso por
índice `0` produce `KeyError(0)`, que en la interfaz se reducía al mensaje
opaco `: 0`.

R8.22E5 corrige la reserva utilizando alias explícitos y acceso por nombre
(`bank_question_id`, `question`). También limita la deduplicación histórica
semántica al mismo tema/subtema y conserva inmutables los registros históricos
de preguntas servidas.

La instalación del hotfix no genera preguntas, no crea nuevos lotes servidos,
no modifica el dominio acumulado y no crea eventos de investigación.

## R8.22E5 - Conciliación de continuidad MBADA

La prueba de runtime posterior al hotfix de `RealDictCursor` reveló una segunda
condición de continuidad: el intento reanudable de práctica podía conservar una
ronda `Inicial` ya superada mientras `student_topic_mastery` registraba más
rondas MBADA completadas.

La conciliación compara `retrieval_count` (rondas MBADA ya calificadas) con la
ronda activa persistida. Si el estado activo está detrás del dominio acumulado y
no contiene un resultado pendiente de mostrar, BunsekiChat inicia la siguiente
ronda, obtiene la dificultad más recientemente servida para el mismo
tema/subtema y aplica la regla adaptativa 80/50 ya existente usando el desempeño
acumulado. Los ítems y respuestas históricos no se eliminan.

Este ajuste preserva la recuperación normal de una ronda realmente
interrumpida: si la ronda activa está por delante del número de rondas
calificadas, no se reconcilia ni se descarta el progreso guardado.


## R8.22E6–E15 - Cierre de prácticas MBADA

La revisión de cinco respuestas se registra en lote en el banco. El dominio
acumulado cuenta preguntas y rondas por separado; ninguna práctica cambia la
nota del pretest o postest ni el nivel oficial del estudiante. La ruta conserva
Avanzado para consolidación tras un resultado bajo y permite reutilizar preguntas
servidas pero no respondidas, respetando la deduplicación de tareas matemáticas.

Cuando se agota el banco, la generación pide lotes de cinco preguntas, reintenta
hasta tres respuestas JSON inválidas y exige verificación antes de servirlas.
Los ítems nuevos sobre bases ortonormales y transformaciones lineales se rechazan
para el subtema Teorema de Pitágoras. El mismo filtro se aplica a preguntas ya
verificadas cuando se selecciona una ronda futura; no altera respuestas ni
registros históricos. El filtro de términos es una protección inicial y el
docente conserva la revisión pedagógica del banco.

La actualización del dominio se serializa por estudiante y metodología y se
protege con el número de ronda. Si una revisión se repite tras una interrupción,
se devuelve el dominio existente sin sumar otra vez; una ronda adelantada falla
de forma explícita. No se crean eventos de investigación en esta etapa.

Prueba de referencia: intento 13, ronda 7 Avanzado, cinco respuestas guardadas,
dos aciertos, 24 de 35 acumulados y tiempo de revisión 3.871 s. El estado
`developing` refleja exactitud acumulada, no una calificación académica.
