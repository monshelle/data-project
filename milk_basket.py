import sqlite3

conn = sqlite3.connect('c:/Dev/minji-db-work/emart.db')
cur = conn.cursor()

q = """
WITH milk_sales AS (
    SELECT DISTINCT si.salesId
    FROM SalesItem si
    JOIN Product p ON si.productBarcode = p.barcode
    WHERE p.name LIKE '%우유%'
)
SELECT
    p.barcode        AS productBarcode,
    p.name           AS productName,
    COUNT(*)         AS coOccurrence
FROM SalesItem si
JOIN milk_sales ms ON si.salesId = ms.salesId
JOIN Product    p  ON si.productBarcode = p.barcode
WHERE p.name NOT LIKE '%우유%'
GROUP BY p.barcode, p.name
ORDER BY coOccurrence DESC
LIMIT 3
"""

cur.execute(q)
rows = cur.fetchall()
print(f"{'순위':<4} {'제품명':<22} {'함께 구매된 횟수':>10}")
print("-" * 40)
for i, r in enumerate(rows, 1):
    print(f"{i:<4} {r[1]:<22} {r[2]:>10}")

conn.close()
