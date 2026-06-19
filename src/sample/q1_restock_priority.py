"""
Q1. 재입고 우선순위 분석
- 재고가 재주문점 이하인 상품을 대상으로
- 최근 30일 일평균 판매량과 현재 재고로 버틸 수 있는 일수를 계산
- Stocks, SalesItem, Sales, Product, Store 조인 + 서브쿼리
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from db_config import DB_PATH
from utils import wl, wr

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

q = """
WITH recent_sales AS (
    SELECT si.productBarcode,
           s.storeId,
           SUM(si.quantity) AS qty_30d
    FROM SalesItem si
    JOIN Sales s ON si.salesId = s.id
    WHERE s.saleDate >= DATE('now', '-30 days')
    GROUP BY si.productBarcode, s.storeId
)
SELECT
    st.name                                        AS storeName,
    p.name                                         AS productName,
    sk.quantity                                    AS stock,
    sk.reorderPoint                                AS reorderPt,
    ROUND(COALESCE(rs.qty_30d, 0) / 30.0, 2)      AS daily_avg,
    CASE
        WHEN COALESCE(rs.qty_30d, 0) = 0 THEN 999
        ELSE ROUND(sk.quantity / (rs.qty_30d / 30.0), 1)
    END                                            AS days_left
FROM Stocks sk
JOIN Store   st ON sk.storeId = st.id
JOIN Product p  ON sk.productBarcode = p.barcode
LEFT JOIN recent_sales rs
       ON rs.productBarcode = sk.productBarcode AND rs.storeId = sk.storeId
WHERE sk.quantity <= sk.reorderPoint
ORDER BY days_left ASC, sk.quantity ASC
"""

cur.execute(q)
rows = cur.fetchall()

print(f"{wl('순위', 4)} {wl('매장', 16)} {wl('상품명', 24)} {wr('재고', 6)} {wr('재주문점', 8)} {wr('일평균', 8)} {wr('남은일수', 8)}")
print("-" * 80)
for i, r in enumerate(rows, 1):
    days = f"{r[5]:.1f}일" if r[5] != 999 else "판매없음"
    print(f"{wl(i, 4)} {wl(r[0], 16)} {wl(r[1], 24)} {wr(r[2], 6)} {wr(r[3], 8)} {wr(f'{r[4]:.2f}', 8)} {wr(days, 8)}")

if not rows:
    print("재입고가 필요한 상품이 없습니다.")
else:
    print(f"\n총 {len(rows)}개 상품이 재입고 필요 상태입니다.")

conn.close()
