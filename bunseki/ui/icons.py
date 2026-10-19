"""Trusted, local 24-unit line icons; no external assets or raw SVG input."""
from html import escape
from types import MappingProxyType
from .theme import PALETTE, FUNCTION_TONES

ICONS = MappingProxyType({
    "home": "<path d=\"m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z\"/><path d=\"M9 21v-8h6v8\"/>",
    "admin": "<path d=\"m12 3 8 4v6c0 4-4 7-8 9-4-2-8-5-8-9V7Z\"/><path d=\"m8 12 3 3 5-6\"/>",
    "users": "<circle cx=\"9\" cy=\"7\" r=\"3\"/><path d=\"M3 21v-2a6 6 0 0 1 12 0v2M16 4a3 3 0 0 1 0 6M19 21v-2a6 6 0 0 0-3-5\"/>",
    "subjects": "<path d=\"M12 5v16M12 5C9 3 5 3 2 4v15c4-1 7 0 10 2 3-2 6-3 10-2V4c-3-1-7-1-10 1Z\"/>",
    "practice": "<path d=\"M12 5a3 3 0 0 0-6-1 4 4 0 0 0-3 6 4 4 0 0 0 0 7 4 4 0 0 0 9 3V5ZM12 5a3 3 0 0 1 6-1 4 4 0 0 1 3 6 4 4 0 0 1 0 7 4 4 0 0 1-9 3\"/><path d=\"M8 8c2 0 4 2 4 4M16 8c-2 0-4 2-4 4M7 17c2 0 3-1 3-3M17 17c-2 0-3-1-3-3\"/>",
    "progress": "<path d=\"M3 3v18h18M7 14l4-4 4 3 6-8\"/>",
    "assessment": "<rect x=\"5\" y=\"4\" width=\"14\" height=\"18\" rx=\"2\"/><rect x=\"9\" y=\"2\" width=\"6\" height=\"4\" rx=\"1\"/><path d=\"m8 13 2 2 6-6M9 18h6\"/>",
    "research": "<path d=\"m9 3 4-1 4 9-4 2-4-10ZM12 14a6 6 0 0 1 7 6H5M5 22h15M8 15a7 7 0 0 0 5 5M13 4l3-1\"/><circle cx=\"6\" cy=\"13\" r=\"2\"/>",
    "alert": "<path d=\"M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4\"/>",
    "settings": "<path d=\"m9 3-1 3-3 1-2 3 2 2-1 3 2 3 3-1 2 3h3l1-3 3-1 2-3-2-2 1-3-2-3-3 1-2-3Z\"/><circle cx=\"12\" cy=\"12\" r=\"3\"/>",
    "logout": "<path d=\"M9 3H4v18h5M9 12h12m-4-4 4 4-4 4\"/>",
    "info": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 11v6M12 7h.01\"/>",
    "error": "<path d=\"m12 3 10 18H2L12 3Z\"/><path d=\"M12 9v5M12 17h.01\"/>",
    "empty": "<path d=\"M3 3h18v18H3ZM3 13h5l2 3h4l2-3h5\"/>",
    "loading": "<path d=\"M12 3a9 9 0 1 1-9 9\"/>"
})
SIZES = (18, 20, 22, 24)

def icon_svg(name: str, *, size: int = 24, label: str | None = None) -> str:
    """Return decorative SVG, or a labelled graphic when label is supplied."""
    if name not in ICONS:
        raise ValueError("Unknown icon")
    if type(size) is not int or size not in SIZES:
        raise ValueError("Icon size must be 18, 20, 22 or 24")
    if label is not None and (not isinstance(label, str) or not label.strip()):
        raise ValueError("Functional icons require a nonempty label")
    color = PALETTE[FUNCTION_TONES[name]]
    a11y = 'aria-hidden="true"' if label is None else 'role="img" aria-label="' + escape(label, quote=True) + '"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="bui-svg" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" focusable="false" {a11y}>'
            + ICONS[name] + '</svg>')

def icon_container(name: str, *, size: int = 24, label: str | None = None) -> str:
    tone = FUNCTION_TONES.get(name)
    if tone is None:
        raise ValueError("Unknown icon")
    return f'<span class="bui-icon bui-tone-{tone}">' + icon_svg(name, size=size, label=label) + '</span>'
