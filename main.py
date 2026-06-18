import sqlite3
import os
import unicodedata
from datetime import datetime
from collections import defaultdict

DB_PATH = 'c:/Dev/minji-db-work/emart.db'

def conn():
    return sqlite3.connect(DB_PATH)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def sep(w=62): print('-' * w)
def dsep(w=62): print('=' * w)

def header(title):
    cls()
    dsep()
    print(f'  {title}')
    dsep()

# ── Unicode-aware column padding ──────────────────────────────
# CJK (Korean, Chinese, Japanese) wide chars occupy 2 terminal
# columns each. Python's built-in f"{s:<N}" counts code-points,
# not display columns, so mixed Korean/ASCII text misaligns.
# wl() / wr() measure display width and pad accordingly.

def _dw(s: str) -> int:
    """Display width of string s (wide chars count as 2)."""
    return sum(2 if unicodedata.east_asian_width(c) in ('W', 'F') else 1
               for c in str(s))

def wl(s, w: int) -> str:
    """Left-align s in a field of display width w."""
    s = str(s)
    return s + ' ' * max(0, w - _dw(s))

def wr(s, w: int) -> str:
    """Right-align s in a field of display width w."""
    s = str(s)
    return ' ' * max(0, w - _dw(s)) + s

def pause():
    input('\n[Enter] to continue...')


# =============================================================
# 1. DBA
# =============================================================
def dba_menu():
    while True:
        header('DBA Management')
        print('  1. Table Statistics')
        print('  2. Stock Status')
        print('  3. Order Summary')
        print('  4. Integrity Check')
        print('  0. Back')
        c = input('\nSelect > ').strip()
        if c == '0': break
        elif c == '1': dba_table_stats()
        elif c == '2': dba_stock_status()
        elif c == '3': dba_order_summary()
        elif c == '4': dba_integrity()

def dba_table_stats():
    db = conn(); cur = db.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = [r[0] for r in cur.fetchall()]
    header('Table Statistics')
    print(f"  {'Table':<20} {'Rows':>8}")
    sep()
    for t in tables:
        cur.execute(f'SELECT COUNT(*) FROM {t}')
        print(f"  {t:<20} {cur.fetchone()[0]:>8,}")
    db.close(); pause()

def dba_stock_status():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT st.name, p.name, sk.quantity, sk.reorderPoint,
               CASE WHEN sk.quantity <= sk.reorderPoint THEN 'Low' ELSE 'OK' END
        FROM Stocks sk
        JOIN Store st ON sk.storeId = st.id
        JOIN Product p ON sk.productBarcode = p.barcode
        ORDER BY (sk.quantity <= sk.reorderPoint) DESC, sk.quantity ASC
    """)
    rows = cur.fetchall()
    header('Stock Status')
    print(f"  {'Store':<16} {'Product':<24} {'Stock':>6} {'Reorder Pt':>10} {'Status':>6}")
    sep()
    for r in rows:
        flag = '!! ' if r[4] == 'Low' else '   '
        print(f"  {flag}{wl(r[0],14)} {wl(r[1],24)} {r[2]:>6} {r[3]:>10} {r[4]:>6}")
    db.close(); pause()

def dba_order_summary():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT ot.id, ot.orderDate, ot.status, s.name, st.name,
               COUNT(oi.productBarcode), SUM(oi.quantity)
        FROM OrderTable ot
        JOIN Supplier s ON ot.supplierId = s.id
        JOIN Store st ON ot.storeId = st.id
        JOIN OrderItem oi ON oi.orderId = ot.id
        GROUP BY ot.id ORDER BY ot.orderDate DESC
    """)
    rows = cur.fetchall()
    header('Order Summary')
    print(f"  {'ID':>4} {'Order Date':>10} {'Status':>11} {'Supplier':<16} {'Store':<14} {'Items':>5} {'Qty':>6}")
    sep()
    for r in rows:
        print(f"  {r[0]:>4} {r[1][:10]:>10} {r[2]:>11} {wl(r[3],16)} {wl(r[4],14)} {r[5]:>5} {r[6]:>6}")
    db.close(); pause()

def dba_integrity():
    db = conn(); cur = db.cursor()
    header('Data Integrity Check')
    checks = [
        ('SalesItem -> Product ref',
         "SELECT COUNT(*) FROM SalesItem si WHERE NOT EXISTS (SELECT 1 FROM Product p WHERE p.barcode=si.productBarcode)"),
        ('Sales -> Store ref',
         "SELECT COUNT(*) FROM Sales s WHERE NOT EXISTS (SELECT 1 FROM Store st WHERE st.id=s.storeId)"),
        ('Stocks -> Product ref',
         "SELECT COUNT(*) FROM Stocks sk WHERE NOT EXISTS (SELECT 1 FROM Product p WHERE p.barcode=sk.productBarcode)"),
        ('OrderItem -> OrderTable ref',
         "SELECT COUNT(*) FROM OrderItem oi WHERE NOT EXISTS (SELECT 1 FROM OrderTable ot WHERE ot.id=oi.orderId)"),
        ('Brand -> Supplier ref',
         "SELECT COUNT(*) FROM Brand b WHERE NOT EXISTS (SELECT 1 FROM Supplier s WHERE s.id=b.supplierId)"),
    ]
    all_ok = True
    for desc, q in checks:
        cur.execute(q)
        cnt = cur.fetchone()[0]
        tag = 'OK' if cnt == 0 else f'!! {cnt}'
        if cnt: all_ok = False
        print(f"  [{tag:>6}]  {desc}")
    print('\n  All checks passed.' if all_ok else '\n  Violations found — please review.')
    db.close(); pause()


# =============================================================
# 2. Distributor OLAP
# =============================================================
def olap_menu():
    while True:
        header('Distributor OLAP Analytics')
        print('  1. Sales Ranking by Store')
        print('  2. Top 10 Products by Revenue')
        print('  3. Sales by Region')
        print('  4. Monthly Sales Trend')
        print('  5. Top 20 Products per Store')
        print('  6. Basket Analysis')
        print('  7. Category Revenue')
        print('  8. Category by Region')
        print('  9. Monthly Category Trend')
        print('  A. Customer Grade Analysis')
        print('  B. Top 20 Products by Region')
        print('  0. Back')
        c = input('\nSelect > ').strip().upper()
        if c == '0': break
        elif c == '1': olap_store_rank()
        elif c == '2': olap_product_top10()
        elif c == '3': olap_region()
        elif c == '4': olap_monthly()
        elif c == '5': olap_top20_per_store()
        elif c == '6': olap_basket()
        elif c == '7': olap_category()
        elif c == '8': olap_region_category()
        elif c == '9': olap_monthly_category()
        elif c == 'A': olap_customer_grade()
        elif c == 'B': olap_top20_per_region()

def olap_store_rank():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT st.name, COUNT(DISTINCT s.id), SUM(si.quantity),
               SUM(si.quantity * si.unitPrice)
        FROM Store st
        JOIN Sales s ON s.storeId = st.id
        JOIN SalesItem si ON si.salesId = s.id
        GROUP BY st.id ORDER BY 4 DESC
    """)
    rows = cur.fetchall()
    header('Sales Ranking by Store')
    print(f"  {'Rank':<4} {'Store':<20} {'Txns':>6} {'Units':>8} {'Revenue':>14}")
    sep()
    for i, r in enumerate(rows, 1):
        print(f"  {i:<4} {wl(r[0],20)} {r[1]:>6} {r[2]:>8} {r[3]:>14,}")
    db.close(); pause()

def olap_product_top10():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT p.name, SUM(si.quantity), SUM(si.quantity * si.unitPrice)
        FROM SalesItem si JOIN Product p ON si.productBarcode = p.barcode
        GROUP BY p.barcode ORDER BY 3 DESC LIMIT 10
    """)
    rows = cur.fetchall()
    header('Top 10 Products by Revenue')
    print(f"  {'Rank':<4} {'Product':<28} {'Units':>8} {'Revenue':>14}")
    sep()
    for i, r in enumerate(rows, 1):
        print(f"  {i:<4} {wl(r[0],28)} {r[1]:>8} {r[2]:>14,}")
    db.close(); pause()

def olap_region():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT st.region, COUNT(DISTINCT s.id), SUM(si.quantity),
               SUM(si.quantity * si.unitPrice)
        FROM Store st JOIN Sales s ON s.storeId = st.id
        JOIN SalesItem si ON si.salesId = s.id
        GROUP BY st.region ORDER BY 4 DESC
    """)
    rows = cur.fetchall()
    header('Sales by Region')
    print(f"  {'Region':<10} {'Txns':>8} {'Units':>8} {'Revenue':>14}")
    sep()
    for r in rows:
        print(f"  {wl(r[0],10)} {r[1]:>8} {r[2]:>8} {r[3]:>14,}")
    db.close(); pause()

def olap_monthly():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT SUBSTR(s.saleDate,1,7) AS m,
               COUNT(DISTINCT s.id), SUM(si.quantity * si.unitPrice)
        FROM Sales s JOIN SalesItem si ON si.salesId = s.id
        GROUP BY m ORDER BY m
    """)
    rows = cur.fetchall()
    if not rows:
        print('  No data.'); pause(); return
    max_rev = max(r[2] for r in rows)
    header('Monthly Sales Trend')
    print(f"  {'Month':<10} {'Txns':>6} {'Revenue':>14}  Chart")
    sep()
    for r in rows:
        bar = '#' * int(r[2] / max_rev * 30)
        print(f"  {r[0]:<10} {r[1]:>6} {r[2]:>14,}  {bar}")
    db.close(); pause()

def olap_top20_per_store():
    db = conn(); cur = db.cursor()
    cur.execute("""
        WITH sps AS (
            SELECT st.id sid, st.name sname, p.barcode bcode, p.name pname,
                   SUM(si.quantity) qty
            FROM Sales s JOIN SalesItem si ON s.id = si.salesId
            JOIN Product p ON si.productBarcode = p.barcode
            JOIN Store st ON s.storeId = st.id
            GROUP BY st.id, p.barcode
        ), ranked AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY sid ORDER BY qty DESC) rnk FROM sps
        )
        SELECT sname, rnk, pname, qty FROM ranked WHERE rnk <= 20 ORDER BY sid, rnk
    """)
    rows = cur.fetchall()
    header('Top 20 Products per Store')
    cur_store = None
    for r in rows:
        if r[0] != cur_store:
            cur_store = r[0]
            print(f'\n  [{cur_store}]')
            print(f"  {'Rank':>4}  {'Product':<28} {'Units':>6}")
            print('  ' + '-' * 42)
        print(f"  {r[1]:>4}  {wl(r[2],28)} {r[3]:>6}")
    db.close(); pause()

def olap_basket():
    db = conn(); cur = db.cursor()
    keyword = input('Base product keyword (e.g. milk) > ').strip() or 'milk'
    cur.execute(f"""
        WITH base AS (
            SELECT DISTINCT si.salesId FROM SalesItem si
            JOIN Product p ON si.productBarcode = p.barcode
            WHERE p.name LIKE ?
        )
        SELECT p.name, COUNT(*) cnt
        FROM SalesItem si JOIN base ON si.salesId = base.salesId
        JOIN Product p ON si.productBarcode = p.barcode
        WHERE p.name NOT LIKE ?
        GROUP BY p.barcode ORDER BY cnt DESC LIMIT 10
    """, (f'%{keyword}%', f'%{keyword}%'))
    rows = cur.fetchall()
    header(f"Products Bought with '{keyword}' - Top 10")
    if not rows:
        print('  No data.')
    else:
        print(f"  {'Rank':<4} {'Product':<28} {'Co-occur':>10}")
        sep()
        for i, r in enumerate(rows, 1):
            print(f"  {i:<4} {wl(r[0],28)} {r[1]:>10}")
    db.close(); pause()

# Category label SQL CASE (shared)
_CAT_CASE = """
    CASE
        WHEN p.barcode LIKE '8801%' THEN 'Staples/Other'
        WHEN p.barcode LIKE '8802%' THEN 'Noodles/Snack (Nongshim)'
        WHEN p.barcode LIKE '8803%' THEN 'Noodles/Curry (Ottogi)'
        WHEN p.barcode LIKE '8804%' THEN 'Snacks (Lotte)'
        WHEN p.barcode LIKE '8805%' THEN 'Beverages (Coca-Cola)'
        WHEN p.barcode LIKE '8806%' THEN 'Dairy (Seoul Milk)'
        WHEN p.barcode LIKE '8807%' THEN 'Tofu/Noodles (Pulmuone)'
        WHEN p.barcode LIKE '8808%' THEN 'Coffee/Cereal (Dongsuh)'
        WHEN p.barcode LIKE '8809%' THEN 'Dairy/Ice Cream (Binggrae)'
        WHEN p.barcode LIKE '8810%' THEN 'Snacks (Orion)'
        ELSE 'Other'
    END
"""

def olap_category():
    db = conn(); cur = db.cursor()
    cur.execute(f"""
        SELECT {_CAT_CASE} AS cat,
               COUNT(DISTINCT s.id)            AS txn,
               SUM(si.quantity)                AS qty,
               SUM(si.quantity * si.unitPrice) AS revenue
        FROM SalesItem si
        JOIN Product p ON si.productBarcode = p.barcode
        JOIN Sales   s ON si.salesId = s.id
        GROUP BY cat ORDER BY revenue DESC
    """)
    rows = cur.fetchall()
    header('Category Revenue')
    print(f"  {'Category':<28} {'Txns':>6} {'Units':>8} {'Revenue':>14}  {'Share':>6}")
    sep()
    total = sum(r[3] for r in rows)
    for r in rows:
        pct = r[3] / total * 100 if total else 0
        print(f"  {r[0]:<28} {r[1]:>6} {r[2]:>8} {r[3]:>14,}  {pct:5.1f}%")
    db.close(); pause()

def olap_region_category():
    db = conn(); cur = db.cursor()
    cur.execute(f"""
        SELECT st.region, {_CAT_CASE} AS cat,
               SUM(si.quantity * si.unitPrice) AS revenue
        FROM SalesItem si
        JOIN Product p ON si.productBarcode = p.barcode
        JOIN Sales   s ON si.salesId = s.id
        JOIN Store  st ON s.storeId = st.id
        GROUP BY st.region, cat
        ORDER BY st.region, revenue DESC
    """)
    rows = cur.fetchall()
    header('Category Sales by Region')
    cur_region = None
    for r in rows:
        if r[0] != cur_region:
            cur_region = r[0]
            print(f'\n  [{cur_region}]')
            print(f"  {'Category':<28} {'Revenue':>14}")
            print('  ' + '-' * 44)
        print(f"  {wl(r[1],28)} {r[2]:>14,}")
    db.close(); pause()

def olap_monthly_category():
    db = conn(); cur = db.cursor()
    cur.execute(f"""
        SELECT SUBSTR(s.saleDate,1,7) AS m,
               {_CAT_CASE} AS cat,
               SUM(si.quantity * si.unitPrice) AS revenue
        FROM SalesItem si
        JOIN Product p ON si.productBarcode = p.barcode
        JOIN Sales   s ON si.salesId = s.id
        GROUP BY m, cat
        ORDER BY m, revenue DESC
    """)
    rows = cur.fetchall()
    header('Monthly Category Trend')
    cur_month = None
    for r in rows:
        if r[0] != cur_month:
            cur_month = r[0]
            print(f'\n  [{cur_month}]')
            print(f"  {'Category':<28} {'Revenue':>14}")
            print('  ' + '-' * 44)
        print(f"  {wl(r[1],28)} {r[2]:>14,}")
    db.close(); pause()

def olap_customer_grade():
    db = conn(); cur = db.cursor()
    cur.execute("""
        WITH cust_stats AS (
            SELECT s.customerId,
                   c.name,
                   COUNT(DISTINCT s.id)            AS visit_cnt,
                   SUM(si.quantity * si.unitPrice) AS total_spend
            FROM Sales s
            JOIN SalesItem si ON si.salesId = s.id
            JOIN Customer   c ON c.id = s.customerId
            GROUP BY s.customerId
        )
        SELECT
            CASE
                WHEN visit_cnt >= 8  THEN 'VIP'
                WHEN visit_cnt >= 4  THEN 'Regular'
                ELSE                      'Low-freq'
            END AS grade,
            COUNT(*)           AS cust_cnt,
            AVG(visit_cnt)     AS avg_visit,
            AVG(total_spend)   AS avg_spend,
            SUM(total_spend)   AS total_revenue
        FROM cust_stats
        GROUP BY grade
        ORDER BY total_revenue DESC
    """)
    rows = cur.fetchall()
    header('Customer Grade Analysis  (VIP: 8+ visits / Regular: 4+ / Low-freq: <4)')
    print(f"  {'Grade':<10} {'Customers':>9} {'Avg Visits':>10} {'Avg Spend':>12} {'Total Revenue':>16}")
    sep()
    for r in rows:
        print(f"  {r[0]:<10} {r[1]:>9} {r[2]:>10.1f} {r[3]:>12,.0f} {r[4]:>16,}")

    cur.execute("""
        SELECT c.name, c.birthday,
               COUNT(DISTINCT s.id)            AS visits,
               SUM(si.quantity * si.unitPrice) AS spend
        FROM Sales s
        JOIN SalesItem si ON si.salesId = s.id
        JOIN Customer   c ON c.id = s.customerId
        GROUP BY s.customerId
        ORDER BY spend DESC LIMIT 10
    """)
    top = cur.fetchall()
    print('\n  Top 10 Customers by Spend')
    print(f"  {'Name':<12} {'Birthday':>10} {'Visits':>6} {'Total Spend':>14}")
    print('  ' + '-' * 46)
    for r in top:
        print(f"  {wl(r[0],12)} {r[1]:>10} {r[2]:>6} {r[3]:>14,}")
    db.close(); pause()

def olap_top20_per_region():
    db = conn(); cur = db.cursor()
    cur.execute("""
        WITH rps AS (
            SELECT st.region,
                   p.barcode,
                   p.name                  AS pname,
                   SUM(si.quantity)        AS qty
            FROM Sales s
            JOIN SalesItem si ON s.id = si.salesId
            JOIN Product   p  ON si.productBarcode = p.barcode
            JOIN Store     st ON s.storeId = st.id
            GROUP BY st.region, p.barcode
        ), ranked AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY region ORDER BY qty DESC) rnk
            FROM rps
        )
        SELECT region, rnk, pname, qty FROM ranked WHERE rnk <= 20
        ORDER BY region, rnk
    """)
    rows = cur.fetchall()
    header('Top 20 Products by Region')
    cur_r = None
    for r in rows:
        if r[0] != cur_r:
            cur_r = r[0]
            print(f'\n  [{cur_r}]')
            print(f"  {'Rank':>4}  {'Product':<28} {'Units':>6}")
            print('  ' + '-' * 42)
        print(f"  {r[1]:>4}  {wl(r[2],28)} {r[3]:>6}")
    db.close(); pause()


# =============================================================
# 3. Customer Interface
# =============================================================
def consumer_menu():
    while True:
        header('Customer Interface')
        print('  1. Product Search')
        print('  2. Stock by Store')
        print('  3. My Purchase History')
        print('  4. Store Info')
        print('  0. Back')
        c = input('\nSelect > ').strip()
        if c == '0': break
        elif c == '1': consumer_search()
        elif c == '2': consumer_stock()
        elif c == '3': consumer_history()
        elif c == '4': consumer_store_info()

def consumer_search():
    kw = input('Search keyword > ').strip()
    if not kw: return
    db = conn(); cur = db.cursor()
    cur.execute(
        "SELECT barcode, name, specification, wrap, price FROM Product WHERE name LIKE ?",
        (f'%{kw}%',)
    )
    rows = cur.fetchall()
    header(f"Search Results: '{kw}'")
    if not rows:
        print('  No results.')
    else:
        print(f"  {'Barcode':<16} {'Product':<28} {'Spec':<8} {'Pack':<6} {'Price':>8}")
        sep()
        for r in rows:
            print(f"  {r[0]:<16} {wl(r[1],28)} {wl(r[2] or '-',8)} {wl(r[3] or '-',6)} {r[4]:>8,}")
    db.close(); pause()

def consumer_stock():
    kw = input('Search keyword > ').strip()
    if not kw: return
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT st.name, p.name, sk.quantity
        FROM Stocks sk
        JOIN Store st ON sk.storeId = st.id
        JOIN Product p ON sk.productBarcode = p.barcode
        WHERE p.name LIKE ? AND sk.quantity > 0
        ORDER BY sk.quantity DESC
    """, (f'%{kw}%',))
    rows = cur.fetchall()
    header(f"Stock Availability: '{kw}'")
    if not rows:
        print('  No stores with stock.')
    else:
        print(f"  {'Store':<20} {'Product':<28} {'Stock':>6}")
        sep()
        for r in rows:
            print(f"  {wl(r[0],20)} {wl(r[1],28)} {r[2]:>6}")
    db.close(); pause()

def consumer_history():
    db = conn(); cur = db.cursor()
    cur.execute('SELECT id, name FROM Customer ORDER BY id')
    customers = cur.fetchall()
    print('\n  Customer List:')
    for c in customers:
        print(f"    {c[0]:>3}. {c[1]}")
    cid = input('\n  Customer ID > ').strip()
    if not cid.isdigit():
        db.close(); return
    cur.execute("""
        SELECT s.id, s.saleDate, st.name, p.name,
               si.quantity, si.unitPrice, si.quantity * si.unitPrice
        FROM Sales s
        JOIN Store st ON s.storeId = st.id
        JOIN SalesItem si ON si.salesId = s.id
        JOIN Product p ON si.productBarcode = p.barcode
        WHERE s.customerId = ?
        ORDER BY s.saleDate DESC, s.id
    """, (int(cid),))
    rows = cur.fetchall()
    header(f'Customer #{cid} - Purchase History')
    if not rows:
        print('  No purchase history.')
    else:
        last_id, sale_total = None, 0
        for r in rows:
            if r[0] != last_id:
                if last_id is not None:
                    print(f"  {'Subtotal':>54}: {sale_total:>10,}")
                    sale_total = 0
                last_id = r[0]
                print(f"\n  [{r[1][:16]}] {r[2]}  (Txn #{r[0]})")
            print(f"    {wl(r[3],28)} {r[4]:>3} x {r[5]:>8,} = {r[6]:>10,}")
            sale_total += r[6]
        print(f"  {'Subtotal':>54}: {sale_total:>10,}")
    db.close(); pause()

def consumer_store_info():
    db = conn(); cur = db.cursor()
    cur.execute('SELECT id, name, address, region, openHour, closeHour FROM Store')
    rows = cur.fetchall()
    header('Store Information')
    for r in rows:
        print(f"  [{r[0]}] {r[1]}  ({r[3]})")
        print(f"       Address : {r[2]}")
        print(f"       Hours   : {r[4]} ~ {r[5]}")
        print()
    db.close(); pause()


# =============================================================
# 4. Auto Reorder
# =============================================================
def reorder_menu():
    while True:
        header('Auto Reorder')
        print('  1. Low Stock Alert')
        print('  2. Create Auto-Order')
        print('  3. Order History')
        print('  0. Back')
        c = input('\nSelect > ').strip()
        if c == '0': break
        elif c == '1': reorder_shortage()
        elif c == '2': reorder_create()
        elif c == '3': reorder_history()

def reorder_shortage():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT st.name, p.name, sk.quantity, sk.reorderPoint,
               sk.reorderPoint - sk.quantity AS gap
        FROM Stocks sk
        JOIN Store st ON sk.storeId = st.id
        JOIN Product p ON sk.productBarcode = p.barcode
        WHERE sk.quantity <= sk.reorderPoint
        ORDER BY gap DESC
    """)
    rows = cur.fetchall()
    header('Low Stock Alert')
    if not rows:
        print('  No low-stock items.')
    else:
        print(f"  {'Store':<20} {'Product':<26} {'Stock':>6} {'Reorder Pt':>10} {'Shortage':>8}")
        sep()
        for r in rows:
            print(f"  {wl(r[0],20)} {wl(r[1],26)} {r[2]:>6} {r[3]:>10} {r[4]:>8}")
        print(f"\n  {len(rows)} item(s) below reorder point")
    db.close(); pause()

def reorder_create():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT sk.storeId, b.supplierId, sk.productBarcode,
               sk.reorderPoint * 2 - sk.quantity AS orderQty,
               st.name, sp.name, p.name
        FROM Stocks sk
        JOIN Product p ON sk.productBarcode = p.barcode
        JOIN Brand b ON p.brandId = b.id
        JOIN Supplier sp ON b.supplierId = sp.id
        JOIN Store st ON sk.storeId = st.id
        WHERE sk.quantity <= sk.reorderPoint
          AND sk.reorderPoint * 2 - sk.quantity > 0
        ORDER BY sk.storeId, b.supplierId
    """)
    rows = cur.fetchall()
    if not rows:
        print('\n  No items to order.')
        db.close(); pause(); return

    orders = defaultdict(list)
    meta = {}
    for r in rows:
        key = (r[0], r[1])
        orders[key].append((r[2], r[3], r[6]))
        meta[key] = (r[4], r[5])

    header('Pending Auto-Order Preview')
    for (sid, sup_id), items in orders.items():
        sname, supname = meta[(sid, sup_id)]
        print(f"\n  Store: {sname}  |  Supplier: {supname}")
        for barcode, qty, pname in items:
            print(f"    {wl(pname,28)} -> {qty:>4} unit(s)")

    confirm = input('\n  Create order? (y/n) > ').strip().lower()
    if confirm != 'y':
        print('  Cancelled.')
        db.close(); pause(); return

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    created = 0
    for (store_id, sup_id), items in orders.items():
        cur.execute(
            "INSERT INTO OrderTable (orderDate, status, supplierId, storeId) VALUES (?,?,?,?)",
            (now, 'PENDING', sup_id, store_id)
        )
        order_id = cur.lastrowid
        for barcode, qty, _ in items:
            cur.execute(
                "INSERT OR IGNORE INTO OrderItem (orderId, productBarcode, quantity, deliveredQuantity) VALUES (?,?,?,0)",
                (order_id, barcode, qty)
            )
        created += 1

    db.commit()
    print(f'\n  {created} order(s) created.')
    db.close(); pause()

def reorder_history():
    db = conn(); cur = db.cursor()

    # Filter options
    header('Order History')
    print('  Filter by status:')
    print('  1. All')
    print('  2. PENDING')
    print('  3. PROCESSING')
    print('  4. COMPLETED')
    print('  5. CANCELLED')
    f = input('\nSelect > ').strip()
    status_filter = {
        '2': ('PENDING',), '3': ('PROCESSING',),
        '4': ('COMPLETED',), '5': ('CANCELLED',),
    }.get(f, None)

    # Summary view: one row per order
    if status_filter:
        cur.execute("""
            SELECT ot.id, ot.orderDate, ot.status,
                   sp.name AS supplier, st.name AS store,
                   COUNT(oi.productBarcode)  AS item_count,
                   SUM(oi.quantity)          AS total_ordered,
                   SUM(oi.deliveredQuantity) AS total_delivered,
                   MAX(oi.deliveredAt)       AS last_delivery
            FROM OrderTable ot
            JOIN Supplier sp ON ot.supplierId = sp.id
            JOIN Store    st ON ot.storeId    = st.id
            JOIN OrderItem oi ON oi.orderId   = ot.id
            WHERE ot.status = ?
            GROUP BY ot.id
            ORDER BY ot.orderDate DESC
        """, status_filter)
    else:
        cur.execute("""
            SELECT ot.id, ot.orderDate, ot.status,
                   sp.name AS supplier, st.name AS store,
                   COUNT(oi.productBarcode)  AS item_count,
                   SUM(oi.quantity)          AS total_ordered,
                   SUM(oi.deliveredQuantity) AS total_delivered,
                   MAX(oi.deliveredAt)       AS last_delivery
            FROM OrderTable ot
            JOIN Supplier sp ON ot.supplierId = sp.id
            JOIN Store    st ON ot.storeId    = st.id
            JOIN OrderItem oi ON oi.orderId   = ot.id
            GROUP BY ot.id
            ORDER BY ot.orderDate DESC
        """)

    orders = cur.fetchall()
    header('Order History')
    if not orders:
        print('  No orders found.')
        db.close(); pause(); return

    print(f"  {'ID':>5} {'Order Date':>16} {'Status':>11} {'Supplier':<16} {'Store':<18} {'Items':>5} {'Ordered':>7} {'Delivered':>9} {'Last Delivery':>13}")
    sep(112)
    for o in orders:
        last_del = o[8][:16] if o[8] else '-'
        print(f"  {o[0]:>5} {o[1][:16]:>16} {o[2]:>11} {wl(o[3],16)} {wl(o[4],18)} {o[5]:>5} {o[6]:>7} {o[7]:>9} {last_del:>13}")

    # Drill-down into a specific order
    print()
    oid = input('  Enter Order ID for details (or Enter to skip) > ').strip()
    if not oid.isdigit():
        db.close(); pause(); return

    cur.execute("""
        SELECT ot.id, ot.orderDate, ot.status,
               sp.name, st.name, st.region
        FROM OrderTable ot
        JOIN Supplier sp ON ot.supplierId = sp.id
        JOIN Store    st ON ot.storeId    = st.id
        WHERE ot.id = ?
    """, (int(oid),))
    meta = cur.fetchone()
    if not meta:
        print('  Order not found.')
        db.close(); pause(); return

    cur.execute("""
        SELECT p.name, oi.quantity, oi.deliveredQuantity,
               oi.deliveredAt,
               oi.deliveredQuantity * p.price AS delivered_value
        FROM OrderItem oi
        JOIN Product p ON oi.productBarcode = p.barcode
        WHERE oi.orderId = ?
        ORDER BY p.name
    """, (int(oid),))
    items = cur.fetchall()

    header(f'Order #{oid} — Detail')
    print(f"  Order Date : {meta[1]}")
    print(f"  Status     : {meta[2]}")
    print(f"  Supplier   : {meta[3]}")
    print(f"  Store      : {meta[4]}  ({meta[5]})")
    sep()
    print(f"  {'Product':<28} {'Ordered':>7} {'Delivered':>9} {'Delivery Time':>18} {'Del. Value':>12}")
    sep()

    total_ord = total_del = total_val = 0
    for it in items:
        del_time = it[3][:16] if it[3] else '-'
        print(f"  {wl(it[0],28)} {it[1]:>7} {it[2]:>9} {del_time:>18} {it[4]:>12,}")
        total_ord += it[1]
        total_del += it[2]
        total_val += it[4] if it[4] else 0

    sep()
    print(f"  {'TOTAL':<28} {total_ord:>7} {total_del:>9} {'':>18} {total_val:>12,}")

    db.close(); pause()


# =============================================================
# 5. Supplier Interface
# =============================================================
def supplier_menu():
    db = conn(); cur = db.cursor()
    cur.execute('SELECT id, name FROM Supplier ORDER BY id')
    suppliers = cur.fetchall()
    db.close()

    header('Supplier Interface')
    print('  Select Supplier:')
    for s in suppliers:
        print(f"    {s[0]}. {s[1]}")
    sid = input('\n  Supplier ID > ').strip()
    if not sid.isdigit(): return
    sid = int(sid)
    sname = next((s[1] for s in suppliers if s[0] == sid), None)
    if not sname:
        print('  Invalid ID.'); return

    while True:
        header(f'Supplier: {sname}')
        print('  1. View Pending Orders')
        print('  2. Process Delivery')
        print('  3. Delivery History')
        print('  0. Back')
        c = input('\nSelect > ').strip()
        if c == '0': break
        elif c == '1': supplier_pending(sid)
        elif c == '2': supplier_deliver(sid)
        elif c == '3': supplier_history(sid)

def supplier_pending(supplier_id):
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT ot.id, ot.orderDate, st.name, p.name, oi.quantity, oi.deliveredQuantity
        FROM OrderTable ot
        JOIN Store st ON ot.storeId = st.id
        JOIN OrderItem oi ON oi.orderId = ot.id
        JOIN Product p ON oi.productBarcode = p.barcode
        WHERE ot.supplierId = ? AND ot.status = 'PENDING'
        ORDER BY ot.orderDate
    """, (supplier_id,))
    rows = cur.fetchall()
    header('Pending Orders')
    if not rows:
        print('  No pending orders.')
    else:
        print(f"  {'OrderID':>7} {'Order Date':>10} {'Store':<16} {'Product':<26} {'Ord':>5} {'Del':>5}")
        sep()
        for r in rows:
            print(f"  {r[0]:>7} {r[1][:10]:>10} {wl(r[2],16)} {wl(r[3],26)} {r[4]:>5} {r[5]:>5}")
    db.close(); pause()

def supplier_deliver(supplier_id):
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT ot.id, ot.orderDate, st.name
        FROM OrderTable ot JOIN Store st ON ot.storeId = st.id
        WHERE ot.supplierId = ? AND ot.status = 'PENDING'
        ORDER BY ot.orderDate
    """, (supplier_id,))
    orders = cur.fetchall()
    if not orders:
        print('\n  No pending orders to process.')
        db.close(); pause(); return

    print('\n  Pending Orders:')
    for o in orders:
        print(f"    Order #{o[0]}  |  {o[1][:10]}  |  {o[2]}")
    oid = input('\n  Order ID to process > ').strip()
    if not oid.isdigit():
        db.close(); return
    oid = int(oid)

    cur.execute("""
        SELECT oi.productBarcode, p.name, oi.quantity, ot.storeId
        FROM OrderItem oi
        JOIN Product p ON oi.productBarcode = p.barcode
        JOIN OrderTable ot ON oi.orderId = ot.id
        WHERE oi.orderId = ? AND ot.supplierId = ?
    """, (oid, supplier_id))
    items = cur.fetchall()
    if not items:
        print('  Order not found.')
        db.close(); pause(); return

    store_id = items[0][3]
    header(f'Process Delivery - Order #{oid}')
    deliver_data = []
    for barcode, pname, order_qty, _ in items:
        raw = input(f"  {wl(pname,28)} (ordered {order_qty:>4}) -> deliver qty: ").strip()
        d_qty = int(raw) if raw.isdigit() else order_qty
        deliver_data.append((barcode, d_qty))

    confirm = input('\n  Confirm delivery? (y/n) > ').strip().lower()
    if confirm != 'y':
        print('  Cancelled.')
        db.close(); pause(); return

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for barcode, d_qty in deliver_data:
        cur.execute("""
            UPDATE OrderItem SET deliveredQuantity = ?, deliveredAt = ?
            WHERE orderId = ? AND productBarcode = ?
        """, (d_qty, now, oid, barcode))
        cur.execute("""
            UPDATE Stocks SET quantity = quantity + ?
            WHERE storeId = ? AND productBarcode = ?
        """, (d_qty, store_id, barcode))

    cur.execute("""
        SELECT COUNT(*) FROM OrderItem
        WHERE orderId = ? AND (deliveredAt IS NULL OR deliveredAt = '')
    """, (oid,))
    status = 'PROCESSING' if cur.fetchone()[0] > 0 else 'COMPLETED'
    cur.execute("UPDATE OrderTable SET status = ? WHERE id = ?", (status, oid))

    db.commit()
    print(f'\n  Delivery confirmed. Order status: {status}')
    db.close(); pause()

def supplier_history(supplier_id):
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT ot.id, ot.status, st.name, p.name,
               oi.quantity, oi.deliveredQuantity, oi.deliveredAt
        FROM OrderTable ot
        JOIN Store st ON ot.storeId = st.id
        JOIN OrderItem oi ON oi.orderId = ot.id
        JOIN Product p ON oi.productBarcode = p.barcode
        WHERE ot.supplierId = ? AND ot.status IN ('COMPLETED', 'PROCESSING')
        ORDER BY oi.deliveredAt DESC
    """, (supplier_id,))
    rows = cur.fetchall()
    header('Delivery History')
    if not rows:
        print('  No delivery history.')
    else:
        print(f"  {'OrderID':>7} {'Status':>11} {'Store':<16} {'Product':<26} {'Ord':>5} {'Del':>5} {'Del Date':>10}")
        sep()
        for r in rows:
            dt = r[6][:10] if r[6] else '-'
            print(f"  {r[0]:>7} {r[1]:>11} {wl(r[2],16)} {wl(r[3],26)} {r[4]:>5} {r[5]:>5} {dt:>10}")
    db.close(); pause()


# =============================================================
# Main
# =============================================================
def main():
    while True:
        header('Emart DB Management System')
        print('  1. DBA Management')
        print('  2. Distributor OLAP')
        print('  3. Customer Interface')
        print('  4. Auto Reorder')
        print('  5. Supplier Interface')
        print('  0. Exit')
        c = input('\nSelect > ').strip()
        if c == '0':
            print('  Exiting...'); break
        elif c == '1': dba_menu()
        elif c == '2': olap_menu()
        elif c == '3': consumer_menu()
        elif c == '4': reorder_menu()
        elif c == '5': supplier_menu()

if __name__ == '__main__':
    main()
