import sqlite3
from db_config import DB_PATH

db = sqlite3.connect(DB_PATH)
cur = db.cursor()
cur.execute("SELECT MAX(id) FROM Sales"); print("Max salesId:", cur.fetchone()[0])
cur.execute("SELECT MAX(id) FROM Customer"); print("Max customerId:", cur.fetchone()[0])
cur.execute("SELECT MAX(id) FROM Store"); print("Max storeId:", cur.fetchone()[0])
cur.execute("SELECT MAX(id) FROM Supplier"); print("Max supplierId:", cur.fetchone()[0])
cur.execute("SELECT MAX(id) FROM Brand"); print("Max brandId:", cur.fetchone()[0])
cur.execute("SELECT barcode, name, price FROM Product ORDER BY barcode")
print("\nProducts:")
for r in cur.fetchall(): print(f"  {r}")
cur.execute("SELECT DISTINCT region FROM Store"); print("\nRegions:", cur.fetchall())
db.close()
