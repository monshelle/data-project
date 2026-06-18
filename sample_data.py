import sqlite3

conn = sqlite3.connect('c:/Dev/minji-db-work/emart.db')
cur = conn.cursor()

for table in ['Store', 'SalesItem', 'Sales', 'Product']:
    print(f"\n=== {table} (first 5) ===")
    cur.execute(f"SELECT * FROM {table} LIMIT 5")
    for row in cur.fetchall():
        print(row)

conn.close()
