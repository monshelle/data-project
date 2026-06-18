import sqlite3

conn = sqlite3.connect('c:/Dev/minji-db-work/emart.db')
cur = conn.cursor()

cur.execute("SELECT barcode, name FROM Product ORDER BY barcode")
for r in cur.fetchall():
    print(r)

conn.close()
