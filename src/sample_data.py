import sqlite3
from db_config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for table in ['Store', 'SalesItem', 'Sales', 'Product']:
    print(f"\n=== {table} (first 5) ===")
    cur.execute(f"SELECT * FROM {table} LIMIT 5")
    for row in cur.fetchall():
        print(row)

conn.close()
