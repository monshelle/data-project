import sqlite3
from db_config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Query 1: 각 매장별 상위 20개 제품
q1 = """
WITH store_product_sales AS (
    SELECT
        st.id            AS storeId,
        st.name          AS storeName,
        p.barcode        AS productBarcode,
        p.name           AS productName,
        SUM(si.quantity) AS totalQuantity
    FROM Sales s
    JOIN SalesItem si ON s.id = si.salesId
    JOIN Product   p  ON si.productBarcode = p.barcode
    JOIN Store     st ON s.storeId = st.id
    GROUP BY st.id, st.name, p.barcode, p.name
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY storeId ORDER BY totalQuantity DESC) AS rank
    FROM store_product_sales
)
SELECT storeId, storeName, rank, productBarcode, productName, totalQuantity
FROM ranked
WHERE rank <= 20
ORDER BY storeId, rank
"""

print("=== Query 1: 각 매장별 상위 20개 제품 ===")
cur.execute(q1)
rows = cur.fetchall()
for r in rows:
    print(r)

# Query 2: 시도별 상위 20개 제품
q2 = """
WITH region_product_sales AS (
    SELECT
        st.region,
        p.barcode        AS productBarcode,
        p.name           AS productName,
        SUM(si.quantity) AS totalQuantity
    FROM Sales s
    JOIN SalesItem si ON s.id = si.salesId
    JOIN Product   p  ON si.productBarcode = p.barcode
    JOIN Store     st ON s.storeId = st.id
    GROUP BY st.region, p.barcode, p.name
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY region ORDER BY totalQuantity DESC) AS rank
    FROM region_product_sales
)
SELECT region, rank, productBarcode, productName, totalQuantity
FROM ranked
WHERE rank <= 20
ORDER BY region, rank
"""

print("\n=== Query 2: 시도별 상위 20개 제품 ===")
cur.execute(q2)
rows = cur.fetchall()
for r in rows:
    print(r)

conn.close()
