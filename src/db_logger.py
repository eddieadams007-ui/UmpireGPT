import sqlite3
import datetime
import uuid
import os

class DBLogger:
    def __init__(self, db_path=os.getenv('DB_PATH', '/home/eddie_adams007/UmpireGPT/data/app_data.db')):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                division TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                response_time FLOAT NOT NULL,
                query_type TEXT NOT NULL,
                api_used TEXT NOT NULL,
                tokens_used INTEGER NOT NULL,
                rule_reference TEXT,
                thumbs_up BOOLEAN,
                thumbs_down BOOLEAN,
                feedback_text TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_interaction(self, query_text, division, response, session_id, response_time, query_type, api_used, tokens_used, rule_reference=None):
        timestamp = datetime.datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO interactions (
                    query_text, division, response, timestamp, session_id, 
                    response_time, query_type, api_used, tokens_used, rule_reference
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (query_text, division, response, timestamp, session_id, 
                  response_time, query_type, api_used, tokens_used, rule_reference))
            conn.commit()
        except Exception as e:
            print(f"Error logging interaction: {e}")
        finally:
            conn.close()
