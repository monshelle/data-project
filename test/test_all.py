"""각 인터페이스의 핵심 쿼리를 non-interactive로 검증"""
import sqlite3
from src.db_config import DB_PATH as DB

def run(label, sql, params=()):
    db = sqlite3.connect(DB)
    cur = db.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    db.close()
    print(f'\n[{label}]  {len(rows)}행')
    for r in rows[:5]:
        print(' ', r)
    if len(rows) > 5:
        print(f'  ... 외 {len(rows)-5}행')
    return rows

# DBA
run('테이블 현황', "SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence'")
run('재고 부족', "SELECT st.name,p.name,sk.quantity,sk.reorderPoint FROM Stocks sk JOIN Store st ON sk.storeId=st.id JOIN Product p ON sk.productBarcode=p.barcode WHERE sk.quantity<=sk.reorderPoint")
run('발주 현황', "SELECT ot.id,ot.status,s.name,st.name FROM OrderTable ot JOIN Supplier s ON ot.supplierId=s.id JOIN Store st ON ot.storeId=st.id ORDER BY ot.id DESC")

# OLAP
run('매장별 매출', "SELECT st.name,SUM(si.quantity*si.unitPrice) FROM Store st JOIN Sales s ON s.storeId=st.id JOIN SalesItem si ON si.salesId=s.id GROUP BY st.id ORDER BY 2 DESC")
run('월별 트렌드', "SELECT SUBSTR(s.saleDate,1,7),SUM(si.quantity*si.unitPrice) FROM Sales s JOIN SalesItem si ON si.salesId=s.id GROUP BY 1 ORDER BY 1")
run('우유 장바구니', """
    WITH base AS (SELECT DISTINCT si.salesId FROM SalesItem si JOIN Product p ON si.productBarcode=p.barcode WHERE p.name LIKE '%우유%')
    SELECT p.name,COUNT(*) FROM SalesItem si JOIN base ON si.salesId=base.salesId JOIN Product p ON si.productBarcode=p.barcode WHERE p.name NOT LIKE '%우유%' GROUP BY p.barcode ORDER BY 2 DESC LIMIT 3
""")

# Consumer
run('제품 검색(라면)', "SELECT barcode,name,price FROM Product WHERE name LIKE '%라면%'")
run('재고 있는 매장(콜라)', "SELECT st.name,p.name,sk.quantity FROM Stocks sk JOIN Store st ON sk.storeId=st.id JOIN Product p ON sk.productBarcode=p.barcode WHERE p.name LIKE '%콜라%' AND sk.quantity>0")
run('고객#1 구매이력', "SELECT s.id,s.saleDate,st.name,p.name,si.quantity FROM Sales s JOIN Store st ON s.storeId=st.id JOIN SalesItem si ON si.salesId=s.id JOIN Product p ON si.productBarcode=p.barcode WHERE s.customerId=1 ORDER BY s.saleDate DESC")

print('\n모든 쿼리 정상 실행 완료.')
