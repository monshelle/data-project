import sqlite3
from db_config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("=== Brand ===")
cur.execute("SELECT * FROM Brand")
for r in cur.fetchall(): print(r)

print("\n=== Supplier ===")
cur.execute("SELECT * FROM Supplier")
for r in cur.fetchall(): print(r)

print("\n=== Stocks (storeId 1, sample) ===")
cur.execute("SELECT * FROM Stocks WHERE storeId = 1 LIMIT 5")
for r in cur.fetchall(): print(r)

print("\n=== Sales (max id) ===")
cur.execute("SELECT MAX(id) FROM Sales")
print(cur.fetchone())

print("\n=== SalesItem (max salesId) ===")
cur.execute("SELECT MAX(salesId) FROM SalesItem")
print(cur.fetchone())

conn.close()
