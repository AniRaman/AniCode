import sqlite3

db_name = "api_analysis.db"

try:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='api';")
    tables = cursor.fetchall()
    conn.close()

    print("Tables in the database:", [table[0] for table in tables])
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
