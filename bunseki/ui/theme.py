"""Immutable design tokens and explicit, scoped stylesheet loading."""
from pathlib import Path
from types import MappingProxyType

PALETTE = MappingProxyType({
    "navy": "#173052", "magenta": "#DF73A0", "blue": "#4C86DB",
    "green": "#33836A", "yellow": "#D6A12D", "violet": "#8462C3",
    "background": "#F6F8FC", "card": "#FFFFFF",
    "ink": "#173052", "muted": "#526175", "line": "#E6EAF2",
    "error": "#B42318",
})
FUNCTION_TONES = MappingProxyType({
    "home": "blue", "admin": "violet", "users": "violet",
    "subjects": "blue", "practice": "magenta", "progress": "green",
    "assessment": "yellow", "research": "violet", "alert": "yellow",
    "settings": "blue", "logout": "navy", "info": "blue",
    "error": "error", "empty": "navy", "loading": "blue",
})
SPACING = MappingProxyType({"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px"})
RADII = MappingProxyType({"small": "10px", "card": "18px", "large": "24px"})
FONT_FAMILY = 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'

def load_css() -> str:
    """Read bundled CSS on demand; no I/O occurs on import."""
    return Path(__file__).with_name("styles.css").read_text(encoding="utf-8")

def stylesheet_html() -> str:
    """Return trusted local CSS; all selectors use the bunseki-ui namespace."""
    declarations = ";".join(f"--bui-{name}:{value}" for name, value in PALETTE.items())
    declarations += ";" + ";".join(f"--bui-space-{name}:{value}" for name, value in SPACING.items())
    declarations += ";" + ";".join(f"--bui-radius-{name}:{value}" for name, value in RADII.items())
    declarations += f";--bui-font:{FONT_FAMILY}"
    return "<style>.bunseki-ui{" + declarations + "}" + load_css() + "</style>"

def inject_styles(renderer=None) -> None:
    """Explicitly render CSS, optionally through a provided markdown renderer.

    Streamlit is imported only when this function is explicitly called without
    a renderer. No session state is read or changed.
    """
    if renderer is None:
        import streamlit as st
        renderer = st.markdown
    renderer(stylesheet_html(), unsafe_allow_html=True)
