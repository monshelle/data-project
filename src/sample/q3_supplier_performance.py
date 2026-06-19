"""
Q3. 공급업체 납품 성과 요약
- 공급업체별 총 주문 건수, 완료 주문, 완료율
- 납품 상품 종류 수, 총 납품 수량
- OrderTable, OrderItem, Supplier, Brand 조인
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from db_config import DB_PATH
from utils import wl, wr

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

q = """
SELECT
    sp.name                                                AS supplierName,
    COUNT(DISTINCT ot.id)                                  AS total_orders,
    COUNT(DISTINCT CASE WHEN ot.status = 'completed' THEN ot.id END) AS done_orders,
    ROUND(
        COUNT(DISTINCT CASE WHEN ot.status = 'completed' THEN ot.id END)
        * 100.0 / NULLIF(COUNT(DISTINCT ot.id), 0), 1
    )                                                      AS completion_rate,
    COUNT(DISTINCT oi.productBarcode)                      AS product_types,
    SUM(oi.quantity)                                       AS total_qty
FROM Supplier sp
LEFT JOIN OrderTable ot ON ot.supplierId = sp.id
LEFT JOIN OrderItem  oi ON oi.orderId    = ot.id
GROUP BY sp.id
ORDER BY total_orders DESC, completion_rate DESC
"""

cur.execute(q)
rows = cur.fetchall()

print(f"{wl('공급업체', 20)} {wr('총주문', 8)} {wr('완료', 6)} {wr('완료율', 8)} {wr('상품종류', 8)} {wr('총납품수량', 12)}")
print("-" * 67)
for r in rows:
    rate = f"{r[3]:.1f}%" if r[3] is not None else "-"
    qty = f"{r[5]:,}" if r[5] else "-"
    print(f"{wl(r[0], 20)} {wr(r[1], 8)} {wr(r[2], 6)} {wr(rate, 8)} {wr(r[4], 8)} {wr(qty, 12)}")

if not rows:
    print("공급업체 데이터가 없습니다.")

conn.close()
