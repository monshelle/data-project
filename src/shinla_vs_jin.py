import sqlite3
from db_config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

q = """
WITH shin AS (
    SELECT s.storeId, SUM(si.quantity) AS qty
    FROM SalesItem si
    JOIN Product p ON si.productBarcode = p.barcode
    JOIN Sales   s ON si.salesId = s.id
    WHERE p.name LIKE '%신라면%'
    GROUP BY s.storeId
),
jin AS (
    SELECT s.storeId, SUM(si.quantity) AS qty
    FROM SalesItem si
    JOIN Product p ON si.productBarcode = p.barcode
    JOIN Sales   s ON si.salesId = s.id
    WHERE p.name LIKE '%진라면%'
    GROUP BY s.storeId
)
SELECT
    st.name                                   AS storeName,
    st.region,
    COALESCE(shin.qty, 0)                     AS shin_qty,
    COALESCE(jin.qty, 0)                      AS jin_qty,
    COALESCE(shin.qty, 0) - COALESCE(jin.qty, 0) AS diff
FROM Store st
LEFT JOIN shin ON st.id = shin.storeId
LEFT JOIN jin  ON st.id = jin.storeId
WHERE COALESCE(shin.qty, 0) > COALESCE(jin.qty, 0)
ORDER BY diff DESC
"""

cur.execute(q)
rows = cur.fetchall()

print(f"{'순위':<4} {'매장명':<16} {'지역':<6} {'신라면':>8} {'진라면':>8} {'차이':>6}")
print("-" * 52)
for i, r in enumerate(rows, 1):
    print(f"{i:<4} {r[0]:<16} {r[1]:<6} {r[2]:>8} {r[3]:>8} {r[4]:>6}")

if not rows:
    print("신라면이 진라면보다 많이 팔린 매장이 없습니다.")

conn.close()
