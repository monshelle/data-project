from datetime import datetime
from utils import conn, wl, header, sep, pause


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
