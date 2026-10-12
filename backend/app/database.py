import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "bikerental.db"
SQL_DIR = BASE_DIR / "sql"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def dict_factory(cursor, row):
    """Convert SQLite row to a Python dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_connection():
    """Create a SQLite connection with foreign keys enabled and dictionary cursor."""
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = dict_factory
    return conn


@contextmanager
def get_db():
    """Context manager for database operations."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(seed: bool = True):
    """Initialize database using schema.sql and optionally seed.sql."""
    schema_file = SQL_DIR / "schema.sql"
    seed_file = SQL_DIR / "seed.sql"

    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db() as conn:
        conn.executescript(schema_sql)

    if seed and seed_file.exists():
        with open(seed_file, "r", encoding="utf-8") as f:
            seed_sql = f.read()
        with get_db() as conn:
            conn.executescript(seed_sql)


if __name__ == "__main__":
    init_database(seed=True)
    print(f"Database successfully initialized at {DB_PATH}")
