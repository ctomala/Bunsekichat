import re
import secrets
import string
import unicodedata
from io import BytesIO

import pandas as pd


OFFICIAL_COHORT_CODE = "COHORTE_INVESTIGACION_CALCULOI_2026"
OFFICIAL_RESEARCH_TITLE = (
    "Efectos de un Tutor Inteligente basado en Inteligencia Artificial Generativa "
    "sobre el Rendimiento Academico en Calculo Diferencial en la Universidad de Guayaquil"
)

REQUIRED_IMPORT_COLUMNS = [
    "cedula",
    "nombres",
    "apellidos",
    "correo",
    "materia",
    "paralelo",
    "jornada",
    "grupo_investigacion",
]

COLUMN_ALIASES = {
    "cedula": {"cedula", "identificacion", "documento", "dni"},
    "nombres": {"nombres", "nombre", "first_names"},
    "apellidos": {"apellidos", "apellido", "last_names"},
    "correo": {"correo", "correo_electronico", "email", "mail"},
    "materia": {"materia", "asignatura", "subject"},
    "curso": {"curso", "nivel", "semestre", "course_level"},
    "paralelo": {"paralelo", "parallel"},
    "jornada": {"jornada", "turno", "shift"},
    "grupo_investigacion": {
        "grupo_investigacion",
        "grupo",
        "research_group",
        "grupo_experimental_control",
    },
    "cohorte": {"cohorte", "cohort"},
}


def _strip_accents(value):
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_column_name(value):
    value = _strip_accents(value).lower().strip()
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def canonical_column_name(value):
    normalized = normalize_column_name(value)
    for canonical, aliases in COLUMN_ALIASES.items():
        if normalized in aliases:
            return canonical
    return normalized


def normalize_person_name(value):
    value = re.sub(r"\s+", " ", str(value or "").strip())
    value = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]", "", value)
    small_words = {"de", "del", "la", "las", "los", "y", "da", "das", "do", "dos"}
    parts = []
    for token in value.lower().split():
        if token in small_words:
            parts.append(token)
        else:
            parts.append("-".join(piece.capitalize() for piece in token.split("-") if piece))
    return " ".join(parts).strip()


def normalize_cedula(value):
    raw = str(value or "").strip()
    if raw.endswith(".0") and raw[:-2].isdigit():
        raw = raw[:-2]
    return re.sub(r"\D", "", raw)


def normalize_email(value):
    return str(value or "").strip().lower()


def normalize_group(value):
    key = _strip_accents(value).lower().strip()
    if key in {"experimental", "experimento", "e"}:
        return "Experimental"
    if key in {"control", "c"}:
        return "Control"
    return ""


def normalize_shift(value):
    key = _strip_accents(value).lower().strip()
    mapping = {
        "matutino": "Matutino",
        "manana": "Matutino",
        "vespertino": "Vespertino",
        "tarde": "Vespertino",
        "nocturno": "Nocturno",
        "noche": "Nocturno",
    }
    return mapping.get(key, str(value or "").strip().title())


def prepare_enrollment_dataframe(raw_df, default_cohort=OFFICIAL_COHORT_CODE, default_course="1"):
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(), pd.DataFrame([{"fila": "", "campo": "archivo", "error": "El archivo no contiene estudiantes."}])

    df = raw_df.copy()
    df.columns = [canonical_column_name(column) for column in df.columns]
    duplicated_columns = [column for column in df.columns if list(df.columns).count(column) > 1]
    if duplicated_columns:
        message = ", ".join(sorted(set(duplicated_columns)))
        return pd.DataFrame(), pd.DataFrame([{"fila": "", "campo": "columnas", "error": f"Existen columnas duplicadas: {message}."}])

    missing = [column for column in REQUIRED_IMPORT_COLUMNS if column not in df.columns]
    if missing:
        return pd.DataFrame(), pd.DataFrame([{
            "fila": "",
            "campo": "columnas",
            "error": "Faltan columnas obligatorias: " + ", ".join(missing),
        }])

    for optional, default in {"curso": default_course, "cohorte": default_cohort}.items():
        if optional not in df.columns:
            df[optional] = default

    records = []
    issues = []
    email_pattern = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    for position, (_, source) in enumerate(df.iterrows(), start=2):
        row = {
            "fila_origen": position,
            "cedula": normalize_cedula(source.get("cedula")),
            "nombres": normalize_person_name(source.get("nombres")),
            "apellidos": normalize_person_name(source.get("apellidos")),
            "correo": normalize_email(source.get("correo")),
            "materia": re.sub(r"\s+", " ", str(source.get("materia") or "").strip()).title(),
            "curso": re.sub(r"\s+", " ", str(source.get("curso") or default_course).strip()).upper(),
            "paralelo": re.sub(r"\s+", "", str(source.get("paralelo") or "").strip()).upper(),
            "jornada": normalize_shift(source.get("jornada")),
            "grupo_investigacion": normalize_group(source.get("grupo_investigacion")),
            "cohorte": str(source.get("cohorte") or default_cohort).strip().upper(),
        }
        row_errors = []
        if len(row["cedula"]) != 10:
            row_errors.append(("cedula", "La cédula debe contener 10 dígitos."))
        if not row["nombres"]:
            row_errors.append(("nombres", "Los nombres son obligatorios."))
        if not row["apellidos"]:
            row_errors.append(("apellidos", "Los apellidos son obligatorios."))
        if not email_pattern.match(row["correo"]):
            row_errors.append(("correo", "El correo no tiene un formato válido."))
        if not row["materia"]:
            row_errors.append(("materia", "La materia es obligatoria."))
        if not row["paralelo"]:
            row_errors.append(("paralelo", "El paralelo es obligatorio."))
        if not row["jornada"]:
            row_errors.append(("jornada", "La jornada es obligatoria."))
        if not row["grupo_investigacion"]:
            row_errors.append(("grupo_investigacion", "Use Experimental o Control."))
        for field, error in row_errors:
            issues.append({"fila": position, "campo": field, "error": error})
        row["errores"] = " | ".join(error for _, error in row_errors)
        records.append(row)

    normalized = pd.DataFrame(records)
    for field in ["cedula", "correo"]:
        duplicated = normalized[field].ne("") & normalized[field].duplicated(keep=False)
        for index in normalized.index[duplicated]:
            position = int(normalized.at[index, "fila_origen"])
            message = f"{field.capitalize()} duplicado dentro del archivo."
            issues.append({"fila": position, "campo": field, "error": message})
            normalized.at[index, "errores"] = " | ".join(filter(None, [normalized.at[index, "errores"], message]))

    normalized["valido"] = normalized["errores"].eq("")
    return normalized, pd.DataFrame(issues, columns=["fila", "campo", "error"])


def generate_temporary_password(length=10):
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    random_part = "".join(secrets.choice(alphabet) for _ in range(max(8, int(length))))
    return f"Bs!{random_part}"


def build_enrollment_template_excel():
    students = pd.DataFrame([
        {
            "cedula": "0912345678",
            "nombres": "Andrea Lucía",
            "apellidos": "Pérez Gómez",
            "correo": "andrea.perez@ug.edu.ec",
            "materia": "Cálculo I",
            "curso": "1",
            "paralelo": "4-A1",
            "jornada": "Matutino",
            "grupo_investigacion": "Experimental",
            "cohorte": OFFICIAL_COHORT_CODE,
        }
    ])
    instructions = pd.DataFrame([
        {"campo": "cedula", "instruccion": "10 dígitos, sin guiones. Formatear la columna como texto."},
        {"campo": "correo", "instruccion": "Correo único por estudiante."},
        {"campo": "grupo_investigacion", "instruccion": "Solo Experimental o Control."},
        {"campo": "cohorte", "instruccion": f"Use {OFFICIAL_COHORT_CODE} para la investigación oficial."},
        {"campo": "seguridad", "instruccion": "La contraseña temporal se genera al matricular y no se almacena en texto plano."},
    ])
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        students.to_excel(writer, sheet_name="Estudiantes", index=False)
        instructions.to_excel(writer, sheet_name="Instrucciones", index=False)
        worksheet = writer.book["Estudiantes"]
        worksheet.freeze_panes = "A2"
        for cell in worksheet["A"]:
            cell.number_format = "@"
        widths = {"A": 16, "B": 24, "C": 24, "D": 32, "E": 20, "F": 12, "G": 14, "H": 16, "I": 24, "J": 42}
        for column, width in widths.items():
            worksheet.column_dimensions[column].width = width
    return output.getvalue()

