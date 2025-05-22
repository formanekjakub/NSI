import sqlite3
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

DB_FILE = 'instance/database.db'
# Use 'db' as the SQLAlchemy instance to match imports
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Raw SQLite operations

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp REAL,
            ts_measure TEXT,
            ts_sent TEXT,
            ts_received TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_record(temp, ts_measure, ts_sent):
    now = datetime.now()
    ts_received = now.strftime('%Y-%m-%d %H:%M:%S') + f'.{now.microsecond//1000:03d}'
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO measurements (temp, ts_measure, ts_sent, ts_received) VALUES (?,?,?,?)',
        (temp, ts_measure, ts_sent, ts_received)
    )
    conn.commit()
    conn.close()


def fetch_all(sort='desc'):
    order = 'DESC' if sort == 'desc' else 'ASC'
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM measurements ORDER BY id {order}')
    rows = cur.fetchall()
    conn.close()
    return rows


def remove_record(rec_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('DELETE FROM measurements WHERE id=?', (rec_id,))
    conn.commit()
    conn.close()


def wipe_records():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('DELETE FROM measurements')
    cur.execute("DELETE FROM sqlite_sequence WHERE name='measurements'")
    conn.commit()
    conn.close()