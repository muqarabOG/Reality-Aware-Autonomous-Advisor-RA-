import sqlite3
import json
from datetime import datetime
import os

class MissionDatabase:
    def __init__(self, db_path="mission_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mission_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                safety_score REAL,
                mae REAL,
                alerts TEXT,
                scene_description TEXT,
                snapshot_path TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_step(self, safety_score, mae, alerts, scene_description, snapshot_path=None):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO mission_logs (safety_score, mae, alerts, scene_description, snapshot_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (safety_score, mae, json.dumps(alerts), scene_description, snapshot_path))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB ERROR] {e}")

    def get_recent_history(self, limit=50):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM mission_logs ORDER BY id DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[DB ERROR] {e}")
            return []
