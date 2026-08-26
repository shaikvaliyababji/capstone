import sqlite3
import os

db_path = "E:/capstone/AI-SmartHome/backend/smarthome.db"
print("DB Exists:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables:", cursor.fetchall())
    cursor.execute("SELECT * FROM devices;")
    print("Devices:", cursor.fetchall())
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
