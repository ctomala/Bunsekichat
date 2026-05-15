# BunsekiChat

Aplicación web en Streamlit para tutor personalizado de matemáticas universitarias.

## 1. Instalación local

```bash
cd bunsekichat_app
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # Mac/Linux
```

Edita `.env` y coloca tu API key gratuita de Google AI Studio:

```env
GEMINI_API_KEY=tu_api_key
SESSION_TIMEOUT_MINUTES=20
ADMIN_USER=admin
ADMIN_PASSWORD=admin123
```

## 2. Ejecutar

```bash
streamlit run app.py
```

Abre la URL local que te muestra Streamlit.

## 3. Publicar en web

Opciones recomendadas:

1. Streamlit Community Cloud: gratis para prototipos públicos.
2. Render.com: opción sencilla con GitHub.
3. VPS con Docker + Nginx para usar `www.BunsekiChat.com`.

Para dominio propio debes comprar el dominio y apuntar DNS al servidor donde publiques la app.

## 4. Producción

Antes de usar con estudiantes reales:
- Cambia `ADMIN_PASSWORD`.
- Usa PostgreSQL en vez de SQLite si habrá muchos usuarios.
- Agrega política de privacidad y consentimiento para GPS.
- Usa HTTPS obligatorio.
- No subas `.env` a GitHub.
