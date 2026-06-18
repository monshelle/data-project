import sqlite3
from src.db_config import DB_PATH

db = sqlite3.connect(DB_PATH)
cur = db.cursor()

print("=== Order Summary (all) ===")
cur.execute("""
    SELECT ot.id, ot.orderDate, ot.status,
           sp.name, st.name,
           COUNT(oi.productBarcode),
           SUM(oi.quantity),
           SUM(oi.deliveredQuantity),
           MAX(oi.deliveredAt)
    FROM OrderTable ot
    JOIN Supplier sp ON ot.supplierId = sp.id
    JOIN Store    st ON ot.storeId    = st.id
    JOIN OrderItem oi ON oi.orderId   = ot.id
    GROUP BY ot.id ORDER BY ot.orderDate DESC LIMIT 5
""")
for r in cur.fetchall():
    print(f"  ID={r[0]} {r[1][:16]} {r[2]:>11} sup={r[3]} store={r[4]} items={r[5]} ord={r[6]} del={r[7]} last_del={r[8]}")

print("\n=== Order #1 Detail ===")
cur.execute("""
    SELECT p.name, oi.quantity, oi.deliveredQuantity,
           oi.deliveredAt, oi.deliveredQuantity * p.price
    FROM OrderItem oi
    JOIN Product p ON oi.productBarcode = p.barcode
    WHERE oi.orderId = 1
""")
for r in cur.fetchall():
    print(f"  {r[0]:<28} ord={r[1]} del={r[2]} at={r[3]} val={r[4]}")

print("\nAll queries OK.")
db.close()
