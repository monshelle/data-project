import sqlite3
from db_config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT barcode, name FROM Product WHERE name LIKE '%우유%' OR name LIKE '%milk%'")
rows = cur.fetchall()
print("우유 관련 제품:")
for r in rows:
    print(r)

conn.close()
