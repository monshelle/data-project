import sqlite3

conn = sqlite3.connect('c:/Dev/minji-db-work/emart.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables:", tables)

for (table,) in tables:
    print(f"\n--- {table} ---")
    cur.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()
    for col in cols:
        print(col)
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print("Row count:", cur.fetchone()[0])

conn.close()
