import sqlite3
import os
from datetime import datetime
import uuid

class DBLogger:
    def __init__(self):
        self.db_path = os.path.join("logs", "app_data.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT,
                    division TEXT,
                    response TEXT,
                    timestamp TEXT,
                    session_id TEXT,
                    response_time REAL,
                    query_type TEXT,
                    api_used TEXT,
                    tokens_used INTEGER,
                    thumbs_up INTEGER,
                    thumbs_down INTEGER,
                    feedback_text TEXT,
                    rule_reference TEXT
                )
            ''')
            conn.commit()

    def log_interaction(self, query_text, division, response, session_id, response_time, query_type, api_used, tokens_used, thumbs_up=None, thumbs_down=None, feedback_text=None, rule_reference=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions (
                    query_text, division, response, timestamp, session_id, response_time,
                    query_type, api_used, tokens_used, thumbs_up, thumbs_down, feedback_text, rule_reference
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                query_text, division, response, datetime.utcnow().isoformat(), session_id, response_time,
                query_type, api_used, tokens_used, thumbs_up, thumbs_down, feedback_text, rule_reference
            ))
            conn.commit()

    def export_to_csv(self, output_path="logs/interactions.csv"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM interactions")
            rows = cursor.fetchall()
            with open(output_path, 'w') as f:
                f.write("id,query_text,division,response,timestamp,session_id,response_time,query_type,api_used,tokens_used,thumbs_up,thumbs_down,feedback_text,rule_reference\n")
                for row in rows:
                    f.write(','.join(str(x) if x is not None else '' for x in row) + '\n')
