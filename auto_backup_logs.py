import os
import sqlite3
import subprocess
from datetime import datetime
import sys

# GCS bucket for backups
BUCKET = "umpgpt_cloudbuild"
BACKUP_FOLDER = "backups"
DB_PATH = "logs/app_data.db"
CSV_PATH = "logs/interactions.csv"

def _create_table():
    """Create interactions table if not exists."""
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

def export_to_csv():
    """Export DB to CSV."""
    _create_table()  # Ensure table exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interactions")
    rows = cursor.fetchall()
    with open(CSV_PATH, 'w') as f:
        f.write("id,query_text,division,response,timestamp,session_id,response_time,query_type,api_used,tokens_used,thumbs_up,thumbs_down,feedback_text,rule_reference\n")
        for row in rows:
            f.write(','.join(str(x) if x is not None else '' for x in row) + '\n')
    conn.close()
    print(f"Exported {len(rows)} rows to {CSV_PATH}")

def upload_to_gcs():
    """Upload CSV to GCS."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    gcs_path = f"gs://{BUCKET}/{BACKUP_FOLDER}/interactions-{timestamp}.csv"
    subprocess.run(["gsutil", "cp", CSV_PATH, gcs_path], check=True)
    print(f"Uploaded to {gcs_path}")

if __name__ == "__main__":
    try:
        export_to_csv()
        upload_to_gcs()
        print("Backup complete—no data loss!")
    except Exception as e:
        print(f"Backup failed: {e}", file=sys.stderr)
        sys.exit(1)
