import sqlite3
from datetime import datetime
from collections import defaultdict

DB = 'c:/Dev/minji-db-work/emart.db'

db = sqlite3.connect(DB)
cur = db.cursor()

# 부족 재고 확인
cur.execute("""
    SELECT sk.storeId, b.supplierId, sk.productBarcode,
           sk.reorderPoint * 2 - sk.quantity AS orderQty,
           st.name, sp.name, p.name
    FROM Stocks sk
    JOIN Product p ON sk.productBarcode = p.barcode
    JOIN Brand b ON p.brandId = b.id
    JOIN Supplier sp ON b.supplierId = sp.id
    JOIN Store st ON sk.storeId = st.id
    WHERE sk.quantity <= sk.reorderPoint AND sk.reorderPoint * 2 - sk.quantity > 0
    LIMIT 3
""")
rows = cur.fetchall()
print(f'부족 재고 샘플 {len(rows)}건')

if rows:
    orders = defaultdict(list)
    meta = {}
    for r in rows:
        key = (r[0], r[1])
        orders[key].append((r[2], r[3], r[6]))
        meta[key] = (r[4], r[5])

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for (store_id, sup_id), items in list(orders.items())[:1]:  # 1건만 테스트
        cur.execute(
            "INSERT INTO OrderTable (orderDate, status, supplierId, storeId) VALUES (?,?,?,?)",
            (now, 'PENDING', sup_id, store_id)
        )
        order_id = cur.lastrowid
        for barcode, qty, pname in items:
            cur.execute(
                "INSERT OR IGNORE INTO OrderItem (orderId, productBarcode, quantity, deliveredQuantity) VALUES (?,?,?,0)",
                (order_id, barcode, qty)
            )
        print(f'발주 생성 성공: OrderTable id={order_id}, storeId={store_id}, supplierId={sup_id}')

    db.rollback()  # 테스트이므로 롤백
    print('롤백 완료 (실제 저장 안 함)')

db.close()
