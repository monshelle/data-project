"""
신라면 vs 진라면: 신라면이 진라면보다 많이 판매된 매장 수 조회
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from db_config import DB_PATH
from utils import wl, wr

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

print(f"{wl('순위', 4)} {wl('매장명', 16)} {wl('지역', 6)} {wr('신라면', 8)} {wr('진라면', 8)} {wr('차이', 6)}")
print("-" * 53)
for i, r in enumerate(rows, 1):
    print(f"{wl(i, 4)} {wl(r[0], 16)} {wl(r[1], 6)} {wr(r[2], 8)} {wr(r[3], 8)} {wr(r[4], 6)}")

if not rows:
    print("신라면이 진라면보다 많이 팔린 매장이 없습니다.")
else:
    print(f"\n신라면 > 진라면 매장 수: {len(rows)}개")

conn.close()
