"""
Q5. 월별 카테고리별 매출 성장률
- 월별, 카테고리별 매출과 전월 대비 성장률 계산
- LAG 윈도우 함수로 전월 매출 참조
- ProductType, Sales, SalesItem, Product 조인
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from db_config import DB_PATH
from utils import wl, wr

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

q = """
WITH monthly_cat AS (
    SELECT
        SUBSTR(s.saleDate, 1, 7)                       AS month,
        COALESCE(pt.name, 'Uncategorized')             AS category,
        SUM(si.quantity * si.unitPrice)                AS revenue
    FROM SalesItem si
    JOIN Sales   s  ON si.salesId = s.id
    JOIN Product p  ON si.productBarcode = p.barcode
    LEFT JOIN ProductType pt ON pt.productBarcode = p.barcode
    GROUP BY month, category
),
with_prev AS (
    SELECT
        month,
        category,
        revenue,
        LAG(revenue) OVER (PARTITION BY category ORDER BY month) AS prev_revenue
    FROM monthly_cat
)
SELECT
    month,
    category,
    revenue,
    prev_revenue,
    CASE
        WHEN prev_revenue IS NULL OR prev_revenue = 0 THEN NULL
        ELSE ROUND((revenue - prev_revenue) * 100.0 / prev_revenue, 1)
    END AS growth_rate
FROM with_prev
ORDER BY month DESC, revenue DESC
"""

cur.execute(q)
rows = cur.fetchall()

cur_month = None
for r in rows:
    if r[0] != cur_month:
        cur_month = r[0]
        print(f"\n[ {cur_month} ]")
        print(f"  {wl('카테고리', 26)} {wr('매출', 14)} {wr('전월매출', 14)} {wr('성장률', 8)}")
        print("  " + "-" * 65)
    growth = f"{r[4]:+.1f}%" if r[4] is not None else "(첫달)"
    prev = f"{r[3]:,}" if r[3] is not None else "-"
    print(f"  {wl(r[1], 26)} {wr(f'{r[2]:,}', 14)} {wr(prev, 14)} {wr(growth, 8)}")

if not rows:
    print("데이터가 없습니다.")

conn.close()
