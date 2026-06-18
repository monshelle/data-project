import sqlite3
db = sqlite3.connect('c:/Dev/minji-db-work/emart.db')
cur = db.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN ('OrderTable','OrderItem')")
for name, sql in cur.fetchall():
    print(f'=== {name} ===')
    print(sql)
    print()
db.close()
