import sqlite3

DB = 'c:/Dev/minji-db-work/emart.db'

CAT_CASE = """
    CASE
        WHEN p.barcode LIKE '8801%' THEN '주식/기타'
        WHEN p.barcode LIKE '8802%' THEN '라면/스낵(농심)'
        WHEN p.barcode LIKE '8803%' THEN '라면/카레(오뚜기)'
        WHEN p.barcode LIKE '8804%' THEN '과자(롯데)'
        WHEN p.barcode LIKE '8805%' THEN '음료(코카콜라)'
        WHEN p.barcode LIKE '8806%' THEN '유제품(서울우유)'
        WHEN p.barcode LIKE '8807%' THEN '두부/면(풀무원)'
        WHEN p.barcode LIKE '8808%' THEN '커피/시리얼(동서)'
        WHEN p.barcode LIKE '8809%' THEN '유제품/빙과(빙그레)'
        WHEN p.barcode LIKE '8810%' THEN '과자(오리온)'
        ELSE '기타'
    END
"""

db = sqlite3.connect(DB)
cur = db.cursor()

print("=== 카테고리별 매출 ===")
cur.execute(f"""
    SELECT {CAT_CASE} AS cat, SUM(si.quantity*si.unitPrice) rev
    FROM SalesItem si JOIN Product p ON si.productBarcode=p.barcode
    JOIN Sales s ON si.salesId=s.id
    GROUP BY cat ORDER BY rev DESC
""")
for r in cur.fetchall(): print(f"  {r[0]:<22} {r[1]:>10,}")

print("\n=== 지역별 매출 ===")
cur.execute("""
    SELECT st.region, COUNT(DISTINCT s.id) txn, SUM(si.quantity*si.unitPrice) rev
    FROM Sales s JOIN SalesItem si ON si.salesId=s.id JOIN Store st ON s.storeId=st.id
    GROUP BY st.region ORDER BY rev DESC
""")
for r in cur.fetchall(): print(f"  {r[0]:<8} 거래:{r[1]:>4}  매출:{r[2]:>10,}")

print("\n=== 고객 등급 ===")
cur.execute("""
    WITH cs AS (
        SELECT s.customerId, COUNT(DISTINCT s.id) v, SUM(si.quantity*si.unitPrice) sp
        FROM Sales s JOIN SalesItem si ON si.salesId=s.id GROUP BY s.customerId
    )
    SELECT CASE WHEN v>=8 THEN 'VIP' WHEN v>=4 THEN '일반' ELSE '저빈도' END grade,
           COUNT(*) cnt, ROUND(AVG(sp)) avg_sp
    FROM cs GROUP BY grade ORDER BY avg_sp DESC
""")
for r in cur.fetchall(): print(f"  {r[0]:<8} {r[1]}명  평균구매액:{r[2]:>10,}")

print("\n=== 월별 트렌드 ===")
cur.execute("""
    SELECT SUBSTR(s.saleDate,1,7) m, SUM(si.quantity*si.unitPrice) rev
    FROM Sales s JOIN SalesItem si ON si.salesId=s.id
    GROUP BY m ORDER BY m
""")
for r in cur.fetchall(): print(f"  {r[0]}  {r[1]:>10,}")

db.close()
print("\n모든 쿼리 정상.")
