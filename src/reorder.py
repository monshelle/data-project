from collections import defaultdict
from datetime import datetime
from utils import conn, wl, header, sep, pause


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
