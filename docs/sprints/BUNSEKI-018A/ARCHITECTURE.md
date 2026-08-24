# Arquitectura objetivo incremental

## Actual

```text
Streamlit app.py
 ├─ UI estudiante / docente
 ├─ session_state + autenticación bcrypt
 ├─ Gemini
 ├─ PostgreSQL/Supabase (SQL embebido)
 ├─ analítica y exportación
 └─ GPS del navegador
```

## Objetivo compatible

```text
UI Streamlit
 ├─ servicios de dominio: identidad, matrícula, currículo, analítica
 ├─ repositorios PostgreSQL con consultas con alcance obligatorio
 ├─ modelo académico (IDs)
 ├─ eventos pedagógicos (referencias opcionales a IDs)
 └─ vistas de investigación seudonimizadas
```

El acceso debe ser deny-by-default: `ADMIN` puede gestionar globalmente; `TEACHER` solo puede consultar recursos a través de su asignación académica; `STUDENT` solo sus matrículas y eventos. `users` mantiene autenticación y se vincula opcionalmente con `teachers` o `students`; nunca se reutiliza un nombre como clave.

Las migraciones han de ser aditivas e idempotentes. La capa nueva debe coexistir con `profiles` mientras se completa la vinculación inequívoca del histórico.
