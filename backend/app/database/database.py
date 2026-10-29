from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).parent / "sight.db"


def get_connection():
    """
    Devuelve una conexión a la base de datos SQLite.
    """
    return sqlite3.connect(DATABASE_PATH)