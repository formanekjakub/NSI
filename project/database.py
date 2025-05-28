from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import sqlite3

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

DB_PATH = 'instance/database.db'

def init_db():
    """Create pots and measurements tables (with pot_id FK)."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Pots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT UNIQUE NOT NULL,
                name TEXT
            )
        ''')
        # Measurements table now has pot_id FK
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pot_id INTEGER NOT NULL,
                temperature REAL,
                humidity REAL,
                soil_moisture INTEGER,
                light INTEGER,
                timestamp_sent TEXT,
                timestamp_received TEXT,
                FOREIGN KEY(pot_id) REFERENCES pots(id)
            )
        ''')
        conn.commit()

def insert_measurement(client_id, temperature, humidity, soil_moisture, light_level, sent_time):
    """
    Ensure the pot exists (by client_id), then insert a measurement tied to it.
    """
    now = datetime.now()
    ts_received = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # 1) Find or create the pot
        cursor.execute('SELECT id FROM pots WHERE client_id = ?', (client_id,))
        row = cursor.fetchone()
        if row:
            pot_id = row[0]
        else:
            cursor.execute(
                'INSERT INTO pots (client_id, name) VALUES (?, ?)',
                (client_id, client_id)  # default name = client_id
            )
            pot_id = cursor.lastrowid
        # 2) Insert the measurement
        cursor.execute('''
            INSERT INTO measurements
              (pot_id, temperature, humidity, soil_moisture, light, timestamp_sent, timestamp_received)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (pot_id, temperature, humidity, soil_moisture, light_level, sent_time, ts_received))
        conn.commit()

def get_all_pots():
    """Return a list of all pots for populating the dropdown."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pots ORDER BY id')
        return [dict(r) for r in cursor.fetchall()]

def get_last_n_measurements(n, sort='desc', pot_id=None):
    """
    Pull the last n measurements, optionally filtered by pot_id.
    """
    order = 'DESC' if sort.lower() == 'desc' else 'ASC'
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if pot_id:
            cursor.execute(f'''
                SELECT * FROM measurements
                WHERE pot_id = ?
                ORDER BY timestamp_received {order}
                LIMIT ?
            ''', (pot_id, n))
        else:
            cursor.execute(f'''
                SELECT * FROM measurements
                ORDER BY timestamp_received {order}
                LIMIT ?
            ''', (n,))
        return [dict(r) for r in cursor.fetchall()]


def delete_measurement(data_id):
    """Delete a single measurement record by ID."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM measurements WHERE id = ?', (data_id,))
        conn.commit()

def clear_measurements():
    """Delete all records and reset auto-increment ID counter."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM measurements")  # Remove all data
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='measurements'")  # Reset autoincrement
        conn.commit()

def _ensure_settings_table():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
          CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
          )""")
        conn.commit()

def get_threshold(default=30000):
    _ensure_settings_table()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key='threshold'")
        row = c.fetchone()
    return int(row[0]) if row else default

def set_threshold(val):
    _ensure_settings_table()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
          INSERT INTO settings(key,value)
          VALUES('threshold',?)
          ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (str(val),))
        conn.commit()
