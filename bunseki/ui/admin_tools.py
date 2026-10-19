"""Headings for existing administrative tools; no controls or backend calls."""
from .cards import section_header

def render_tools_heading(st):
    st.markdown(section_header("Herramientas administrativas", "Banco IA de práctica, asignaciones docentes y restablecimiento de contraseñas.", icon="settings"), unsafe_allow_html=True)
