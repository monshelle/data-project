import sqlite3
from db_config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT barcode, name FROM Product ORDER BY barcode")
for r in cur.fetchall():
    print(r)

conn.close()
