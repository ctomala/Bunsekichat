"""Pure HTML presentation. Caller text is always escaped, never trusted markup."""
from html import escape
from .icons import icon_container

def _text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Display content must be text")
    return escape(value, quote=True)

def _card(title: str, body: str, *, tone: str, icon: str, tag: str = "") -> str:
    badge = f'<span class="bui-tag">{_text(tag)}</span>' if tag else ""
    return (f'<article class="bunseki-ui bui-card bui-tone-{tone}">'
            '<div class="bui-card-heading">' + icon_container(icon)
            + '<div>' + badge + f'<h3 class="bui-title">{_text(title)}</h3></div></div>'
            + f'<p class="bui-body">{_text(body)}</p></article>')

def academic_card(title: str, body: str) -> str:
    return _card(title, body, tone="blue", icon="subjects", tag="Académico")

def practice_card(title: str, body: str) -> str:
    return _card(title, body, tone="magenta", icon="practice", tag="Práctica adaptativa")

def progress_card(title: str, body: str) -> str:
    """Indicators are supplied as text; this component computes no progress."""
    return _card(title, body, tone="green", icon="progress", tag="Progreso")

def alert_card(title: str, body: str) -> str:
    return _card(title, body, tone="yellow", icon="alert", tag="Aviso")

def admin_card(title: str, body: str, *, icon: str = "admin") -> str:
    if icon not in ("admin", "users", "research"):
        raise ValueError("Administrative icon must be admin, users or research")
    return _card(title, body, tone="violet", icon=icon, tag="Administración")

def error_card(title: str, body: str) -> str:
    return _card(title, body, tone="error", icon="error", tag="Error")

def empty_state(title: str = "Sin información", body: str = "No hay elementos para mostrar.") -> str:
    return _card(title, body, tone="navy", icon="empty", tag="Estado vacío")

def loading_state(body: str = "Preparando la información.") -> str:
    return '<div class="bunseki-ui" role="status" aria-live="polite">' + _card(
        "Cargando", body, tone="blue", icon="loading", tag="Estado de carga") + '</div>'

def section_header(title: str, subtitle: str = "", *, icon: str = "home") -> str:
    return ('<header class="bunseki-ui bui-section-heading">' + icon_container(icon)
            + f'<div><h2 class="bui-section-title">{_text(title)}</h2>'
            + f'<p class="bui-subtitle">{_text(subtitle)}</p></div></header>')

def information(body: str) -> str:
    return ('<aside class="bunseki-ui bui-information">' + icon_container("info", size=20)
            + f'<p><strong>Información.</strong> {_text(body)}</p></aside>')
