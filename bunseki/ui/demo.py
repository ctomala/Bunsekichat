"""Offline component gallery. Run as python -m bunseki.ui.demo --output PATH."""
from html import escape
from .theme import PALETTE, FUNCTION_TONES, stylesheet_html
from .icons import ICONS, icon_container
from .cards import (academic_card, practice_card, progress_card, alert_card,
                    admin_card, error_card, empty_state, loading_state,
                    section_header, information)

LABELS = {
    "home": "Inicio", "admin": "Administración", "users": "Usuarios",
    "subjects": "Asignaturas", "practice": "Práctica adaptativa",
    "progress": "Progreso", "assessment": "Evaluaciones", "research": "Investigación",
    "alert": "Alertas", "settings": "Configuración", "logout": "Cerrar sesión",
    "info": "Información", "error": "Error", "empty": "Estado vacío", "loading": "Carga",
}
def demo_html() -> str:
    palette = "".join(
        f'<div class="bui-palette-item"><div class="bui-swatch" style="background:{PALETTE[k]}" aria-hidden="true"></div>'
        f'<p class="bui-palette-label"><strong>{escape(label)}</strong><br>{PALETTE[k]}</p></div>'
        for k, label in (("navy","Azul principal"),("magenta","Magenta suave"),
                         ("blue","Azul secundario"),("green","Verde"),("yellow","Amarillo"),
                         ("violet","Violeta"),("background","Fondo"),("card","Tarjetas")))
    icons = "".join(
        '<div class="bui-icon-item">' + icon_container(name, size=(18,20,22,24)[i % 4])
        + f'<div><strong>{LABELS[name]}</strong><small>{(18,20,22,24)[i % 4]} px · {FUNCTION_TONES[name]}</small></div></div>'
        for i,name in enumerate(ICONS))
    examples = "".join([
        academic_card("Una base para aprender", "Contenido demostrativo. Esta tarjeta no consulta asignaturas ni datos académicos."),
        practice_card("Aprender a tu ritmo", "Ejemplo visual de práctica adaptativa. No inicia rondas ni ejecuta MBADA."),
        progress_card("Cada paso cuenta", "Indicador demostrativo: 3 de 5 actividades. No representa el progreso de una persona."),
        alert_card("Actividad pendiente", "Aviso demostrativo. La etiqueta y el texto comunican el estado además del color."),
        admin_card("Organización académica", "Ejemplo del espacio administrador. No gestiona usuarios ni modifica asignaciones."),
        error_card("No se pudo cargar", "Error simulado para revisar legibilidad. No se ha realizado una conexión."),
    ])
    states = empty_state(body="Ejemplo demostrativo: aún no hay elementos en esta sección.") + loading_state("Estado visual simulado; no hay procesos en ejecución.")
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; base-uri \'none\'">'
            '<title>BunsekiChat · Galería UI/UX 02.3</title>' + stylesheet_html()
            + '</head><body><main class="bunseki-ui bui-demo">'
            '<span class="bui-demo-tag">UI/UX 02.3 · Demostración aislada</span>'
            '<h1 class="bui-demo-title">Una identidad compartida.<br>Tres espacios para aprender.</h1>'
            '<p class="bui-demo-intro">Administrador, docente y estudiante comparten una base visual clara. '
            'Todos los contenidos de esta galería son ficticios. No hay autenticación, base de datos ni funciones académicas activas.</p>'
            '<nav class="bui-nav" aria-label="Secciones de la galería">'
            '<a href="#palette">Paleta</a><a href="#icons">Iconos</a><a href="#cards">Tarjetas</a><a href="#states">Estados</a></nav>'
            '<section id="palette">' + section_header("Colores que orientan", "Paleta aprobada; colores sólidos.", icon="subjects")
            + '<div class="bui-palette">' + palette + '</div></section>'
            '<section id="icons">' + section_header("Iconografía con propósito", "Trazos de 2 px. Tamaños: 18, 20, 22 y 24 px.", icon="research")
            + '<div class="bui-icon-catalog">' + icons + '</div></section>'
            '<section id="cards">' + section_header("Tarjetas para cada contexto", "Superficies blancas y un filo de color por tarjeta.", icon="admin")
            + '<div class="bui-grid">' + examples + '</div></section>'
            '<section id="states">' + section_header("Estados comprensibles", "La información se expresa con texto, además del color.", icon="info")
            + '<div class="bui-grid">' + states + '</div></section>'
            + information("Los iconos azul, magenta y amarillo usan una base azul oscuro para mantener contraste gráfico. "
                          "El resto conserva fondos suaves. Esta galería no reemplaza los logos existentes.")
            + '</main></body></html>')

def main() -> None:
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(demo_html())

if __name__ == "__main__":
    main()
