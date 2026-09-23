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
