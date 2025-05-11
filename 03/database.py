import sqlite3
from datetime import datetime

DB_PATH = 'instance/database.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                timestamp_measurement TEXT,
                timestamp_sent TEXT,
                timestamp_received TEXT
            )
        ''')
        conn.commit()

def insert_measurement(temperature, timestamp_measurement, timestamp_sent):
    now = datetime.now()
    timestamp_received = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO measurements (temperature, timestamp_measurement, timestamp_sent, timestamp_received)
            VALUES (?, ?, ?, ?)
        ''', (temperature, timestamp_measurement, timestamp_sent, timestamp_received))
        conn.commit()

def get_all_measurements():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM measurements ORDER BY id DESC')
        return cursor.fetchall()


def clear_measurements():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM measurements")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='measurements'")
        conn.commit()
