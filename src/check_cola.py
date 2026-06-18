import sqlite3
from db_config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT barcode, name, price FROM Product WHERE name LIKE '%콜라%' OR name LIKE '%cola%' OR name LIKE '%pepsi%' OR name LIKE '%펩시%'")
rows = cur.fetchall()
print("콜라 관련 제품:")
for r in rows:
    print(r)

conn.close()
