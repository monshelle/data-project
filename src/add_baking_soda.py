"""
베이킹소다 데이터 추가
- Brand    id=20  : CJ 베이킹소다  (supplierId=1, CJ제일제당)
- Product  barcode=881100000001 : 베이킹소다 500g
- Stocks   전 매장(1~10) 재고 추가
- Sales    40건 추가 (id 633~)

ProductType 등록은 migrate_product_type.py 에서 일괄 처리:
  제과제빵재료(leaf) → 식품재료 → 식품   (제과제빵 용도)
  세제/클리너(leaf)  → 청소용품 → 주방용품 (청소 용도)
"""

import sqlite3
import random
from datetime import datetime, timedelta
from db_config import DB_PATH

random.seed(99)
db = sqlite3.connect(DB_PATH)
cur = db.cursor()

BARCODE = '881100000001'
PRICE   = 2500

# ── 1. Brand ──────────────────────────────────────────────────
cur.execute("INSERT INTO Brand VALUES (?,?,?)", (20, 'CJ 베이킹소다', 1))

# ── 2. Product ────────────────────────────────────────────────
cur.execute("INSERT INTO Product VALUES (?,?,?,?,?,?)",
            (BARCODE, '베이킹소다 500g', '500g', '봉지', PRICE, 20))

# ── 3. Stocks (전 매장) ───────────────────────────────────────
stocks = [(sid, BARCODE, random.randint(30, 120), 10) for sid in range(1, 11)]
cur.executemany("INSERT OR IGNORE INTO Stocks VALUES (?,?,?,?)", stocks)

# ── 4. Sales (40건) ───────────────────────────────────────────
cur.execute("SELECT MAX(id) FROM Sales")
sale_id = cur.fetchone()[0] + 1

cur.execute("SELECT id FROM Customer")
cust_ids = [r[0] for r in cur.fetchall()]

start_dt = datetime(2026, 1, 1, 9, 0)
end_dt   = datetime(2026, 6, 18, 22, 59)
total_secs = int((end_dt - start_dt).total_seconds())

sales_rows = []
item_rows  = []

for _ in range(40):
    store_id    = random.randint(1, 10)
    customer_id = random.choice(cust_ids)
    offset      = random.randint(0, total_secs)
    sale_dt     = start_dt + timedelta(seconds=offset)
    if not (9 <= sale_dt.hour <= 22):
        sale_dt = sale_dt.replace(hour=random.randint(10, 21))

    qty   = random.randint(1, 3)
    total = qty * PRICE

    sales_rows.append((sale_id, sale_dt.strftime('%Y-%m-%d %H:%M:%S'), total, customer_id, store_id))
    item_rows.append((sale_id, BARCODE, qty, PRICE))
    sale_id += 1

cur.executemany("INSERT INTO Sales VALUES (?,?,?,?,?)", sales_rows)
cur.executemany("INSERT INTO SalesItem VALUES (?,?,?,?)", item_rows)

db.commit()
db.close()

print("베이킹소다 데이터 추가 완료")
print(f"  Brand     : CJ 베이킹소다 (id=20)")
print(f"  Product   : 베이킹소다 500g (barcode={BARCODE})")
print(f"  ProductType: migrate_product_type.py 에서 등록")
print(f"  Stocks    : 10개 매장")
print(f"  Sales     : {len(sales_rows)}건 추가")
