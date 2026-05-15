import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()
SQLITE_DB = os.getenv("SQLITE_DB", "bunsekichat.db")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
TABLES = ["users", "profiles", "interactions", "location_events", "quizzes", "settings"]

def pg_conn():
    if not DATABASE_URL:
        raise RuntimeError("Falta DATABASE_URL en .env")
    kwargs = {"cursor_factory": RealDictCursor}
    if "sslmode=" not in DATABASE_URL.lower():
        kwargs["sslmode"] = "require"
    c = psycopg2.connect(DATABASE_URL, **kwargs)
    c.autocommit = True
    return c

def sqlite_rows(table):
    sc = sqlite3.connect(SQLITE_DB)
    sc.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in sc.execute(f"SELECT * FROM {table}").fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        sc.close()

def table_columns_pg(cur, table):
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position", (table,))
    return [r["column_name"] for r in cur.fetchall()]

def normalize_value(table, col, value):
    if table == "users" and col == "active":
        return bool(value) if value is not None else True
    return value

def insert_rows(cur, table, rows):
    if not rows:
        print(f"{table}: 0 filas")
        return
    pg_cols = table_columns_pg(cur, table)
    processed = 0
    for row in rows:
        cols = [c for c in row.keys() if c in pg_cols]
        vals = [normalize_value(table, c, row.get(c)) for c in cols]
        placeholders = ",".join(["%s"] * len(cols))
        col_sql = ",".join(cols)
        if table == "users":
            conflict = "ON CONFLICT (id) DO UPDATE SET " + ",".join([f"{c}=EXCLUDED.{c}" for c in cols if c != "id"])
        elif table == "profiles":
            conflict = "ON CONFLICT (user_id) DO UPDATE SET " + ",".join([f"{c}=EXCLUDED.{c}" for c in cols if c != "user_id"])
        elif table == "settings":
            conflict = "ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value"
        else:
            conflict = "ON CONFLICT (id) DO NOTHING" if "id" in cols else ""
        cur.execute(f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders}) {conflict}", vals)
        processed += 1
    print(f"{table}: {processed} filas procesadas")

def reset_sequences(cur):
    for table in ["users", "interactions", "location_events", "quizzes"]:
        cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1), true)")

def main():
    if not Path(SQLITE_DB).exists():
        raise FileNotFoundError(f"No existe {SQLITE_DB}")
    pc = pg_conn()
    try:
        with pc.cursor() as cur:
            for table in TABLES:
                insert_rows(cur, table, sqlite_rows(table))
            reset_sequences(cur)
    finally:
        pc.close()
    print("Migración finalizada correctamente.")

if __name__ == "__main__":
    main()
