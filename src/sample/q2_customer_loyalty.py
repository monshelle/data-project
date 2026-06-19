"""
Q2. 매장별 고객 충성도 분석
- 매장별 전체 고객 수, 재방문(2회 이상) 고객 수, 충성 고객 비율
- 1인당 평균 구매액 계산
- CTE + GROUP BY + HAVING + 윈도우 없는 집계
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from db_config import DB_PATH
from utils import wl, wr

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

q = """
WITH cust_per_store AS (
    SELECT s.storeId,
           s.customerId,
           COUNT(DISTINCT s.id)            AS visit_cnt,
           SUM(si.quantity * si.unitPrice) AS total_spend
    FROM Sales s
    JOIN SalesItem si ON si.salesId = s.id
    WHERE s.customerId IS NOT NULL
    GROUP BY s.storeId, s.customerId
)
SELECT
    st.name                                        AS storeName,
    st.region,
    COUNT(*)                                       AS total_customers,
    SUM(CASE WHEN cps.visit_cnt >= 2 THEN 1 ELSE 0 END) AS loyal_customers,
    ROUND(
        SUM(CASE WHEN cps.visit_cnt >= 2 THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1
    )                                              AS loyalty_rate,
    ROUND(AVG(cps.total_spend), 0)                AS avg_spend_per_customer
FROM cust_per_store cps
JOIN Store st ON cps.storeId = st.id
GROUP BY st.id
ORDER BY loyalty_rate DESC
"""

cur.execute(q)
rows = cur.fetchall()

print(f"{wl('매장명', 18)} {wl('지역', 8)} {wr('전체고객', 8)} {wr('충성고객', 8)} {wr('충성률', 8)} {wr('1인평균구매', 14)}")
print("-" * 69)
for r in rows:
    print(f"{wl(r[0], 18)} {wl(r[1], 8)} {wr(r[2], 8)} {wr(r[3], 8)} {wr(f'{r[4]:.1f}%', 8)} {wr(f'{r[5]:,.0f}', 14)}")

if not rows:
    print("데이터가 없습니다.")
else:
    total_cust = sum(r[2] for r in rows)
    total_loyal = sum(r[3] for r in rows)
    print(f"\n전체 고객 {total_cust:,}명 중 재방문 고객 {total_loyal:,}명 "
          f"({total_loyal/total_cust*100:.1f}%)")

conn.close()
