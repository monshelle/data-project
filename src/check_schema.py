import sqlite3
from db_config import DB_PATH

db = sqlite3.connect(DB_PATH)
cur = db.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN ('OrderTable','OrderItem')")
for name, sql in cur.fetchall():
    print(f'=== {name} ===')
    print(sql)
    print()
db.close()
