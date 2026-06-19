"""
Q4. 베스트셀러 재고 커버리지 분석
- 전체 판매 상위 20개 제품의 현재 매장별 총 재고와 30일 판매 속도를 비교
- 재고가 며칠 치인지(커버리지 일수) 계산
- CTE + ROW_NUMBER 윈도우 함수 + 다중 조인
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from db_config import DB_PATH
from utils import wl, wr

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

q = """
WITH total_sales AS (
    SELECT si.productBarcode,
           SUM(si.quantity) AS total_qty,
           SUM(si.quantity * si.unitPrice) AS total_revenue
    FROM SalesItem si
    GROUP BY si.productBarcode
),
top20 AS (
    SELECT productBarcode, total_qty, total_revenue,
           ROW_NUMBER() OVER (ORDER BY total_qty DESC) AS rank
    FROM total_sales
    LIMIT 20
),
recent_30d AS (
    SELECT si.productBarcode,
           SUM(si.quantity) AS qty_30d
    FROM SalesItem si
    JOIN Sales s ON si.salesId = s.id
    WHERE s.saleDate >= DATE('now', '-30 days')
    GROUP BY si.productBarcode
),
current_stock AS (
    SELECT productBarcode, SUM(quantity) AS total_stock
    FROM Stocks
    GROUP BY productBarcode
)
SELECT
    t.rank,
    p.name                                              AS productName,
    t.total_qty                                         AS total_sold,
    t.total_revenue                                     AS revenue,
    COALESCE(cs.total_stock, 0)                         AS current_stock,
    ROUND(COALESCE(r.qty_30d, 0) / 30.0, 2)            AS daily_avg,
    CASE
        WHEN COALESCE(r.qty_30d, 0) = 0 THEN 999
        ELSE ROUND(COALESCE(cs.total_stock, 0) / (r.qty_30d / 30.0), 1)
    END                                                 AS stock_days
FROM top20 t
JOIN Product p ON t.productBarcode = p.barcode
LEFT JOIN recent_30d  r  ON r.productBarcode = t.productBarcode
LEFT JOIN current_stock cs ON cs.productBarcode = t.productBarcode
ORDER BY t.rank
"""

cur.execute(q)
rows = cur.fetchall()

print(f"{wl('순위', 4)} {wl('상품명', 28)} {wr('총판매', 8)} {wr('매출', 14)} {wr('현재재고', 8)} {wr('일평균', 8)} {wr('재고일수', 8)}")
print("-" * 84)
for r in rows:
    days = f"{r[6]:.1f}일" if r[6] != 999 else "판매없음"
    print(f"{wl(r[0], 4)} {wl(r[1], 28)} {wr(f'{r[2]:,}', 8)} {wr(f'{r[3]:,}', 14)} {wr(f'{r[4]:,}', 8)} {wr(f'{r[5]:.2f}', 8)} {wr(days, 8)}")

if not rows:
    print("판매 데이터가 없습니다.")

conn.close()
