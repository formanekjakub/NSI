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
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                humidity REAL,
                soil_moisture INTEGER,
                light INTEGER,
                timestamp_sent TEXT,
                timestamp_received TEXT
            )
        ''')
        conn.commit()

def insert_measurement(temperature, humidity, soil_moisture, light_level, sent_time):
    now = datetime.now()
    timestamp_received = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO measurements
              (temperature, humidity, soil_moisture, light, timestamp_sent, timestamp_received)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (temperature, humidity, soil_moisture, light_level, sent_time, timestamp_received))
        conn.commit()

def get_all_measurements(sort='desc'):
    order = 'DESC' if sort == 'desc' else 'ASC'
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM measurements ORDER BY id {order}')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


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

def get_last_n_measurements(n, sort='desc'):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    order_clause = 'DESC' if sort == 'desc' else 'ASC'
    cur.execute(f'''
        SELECT * FROM measurements
        ORDER BY timestamp_received {order_clause}
        LIMIT ?
    ''', (n,))

    rows = cur.fetchall()
    conn.close()
    return rows