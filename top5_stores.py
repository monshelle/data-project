import sqlite3

conn = sqlite3.connect('c:/Dev/minji-db-work/emart.db')
cur = conn.cursor()

q = """
SELECT
    st.id                    AS storeId,
    st.name                  AS storeName,
    st.region,
    COUNT(DISTINCT s.id)     AS totalTransactions,
    SUM(si.quantity)         AS totalQuantitySold,
    SUM(si.quantity * si.unitPrice) AS totalRevenue
FROM Store st
JOIN Sales     s  ON s.storeId = st.id
JOIN SalesItem si ON si.salesId = s.id
GROUP BY st.id, st.name, st.region
ORDER BY totalRevenue DESC
LIMIT 5
"""

cur.execute(q)
rows = cur.fetchall()
print(f"{'순위':<4} {'매장명':<16} {'지역':<6} {'거래건수':>8} {'판매수량':>8} {'매출액':>12}")
print("-" * 60)
for i, r in enumerate(rows, 1):
    print(f"{i:<4} {r[1]:<16} {r[2]:<6} {r[3]:>8} {r[4]:>8} {r[5]:>12,}")

conn.close()
