from utils import conn, wl, header, sep, pause


def dba_menu():
    while True:
        header('DBA Management')
        print('  1. Table Statistics')
        print('  2. Stock Status')
        print('  3. Order Summary')
        print('  4. Integrity Check')
        print('  5. Product Type Management')
        print('  0. Back')
        c = input('\nSelect > ').strip()
        if c == '0': break
        elif c == '1': dba_table_stats()
        elif c == '2': dba_stock_status()
        elif c == '3': dba_order_summary()
        elif c == '4': dba_integrity()
        elif c == '5': dba_product_type_menu()


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
# Product Type Management
# =============================================================
def dba_product_type_menu():
    while True:
        header('Product Type Management')
        print('  1. List All Types')
        print('  2. Types by Product')
        print('  3. Add Type to Product')
        print('  4. Remove Type from Product')
        print('  0. Back')
        c = input('\nSelect > ').strip()
        if c == '0': break
        elif c == '1': dba_pt_list_all()
        elif c == '2': dba_pt_list_by_product()
        elif c == '3': dba_pt_add()
        elif c == '4': dba_pt_remove()


def dba_pt_list_all():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT pt.name, COUNT(pt.productBarcode) AS cnt
        FROM ProductType pt
        GROUP BY pt.name
        ORDER BY pt.name
    """)
    rows = cur.fetchall()
    header('All Product Types')
    if not rows:
        print('  No product types defined.')
    else:
        print(f"  {'Type Name':<30} {'# Products':>10}")
        sep()
        for r in rows:
            print(f"  {wl(r[0],30)} {r[1]:>10}")
    db.close(); pause()


def dba_pt_list_by_product():
    kw = input('Product name keyword > ').strip()
    if not kw: return
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT p.barcode, p.name,
               GROUP_CONCAT(pt.name, ', ') AS types
        FROM Product p
        LEFT JOIN ProductType pt ON pt.productBarcode = p.barcode
        WHERE p.name LIKE ?
        GROUP BY p.barcode
        ORDER BY p.name
    """, (f'%{kw}%',))
    rows = cur.fetchall()
    header(f"Product Types: '{kw}'")
    if not rows:
        print('  No products found.')
    else:
        print(f"  {'Product':<30} {'Types'}")
        sep()
        for r in rows:
            print(f"  {wl(r[1],30)} {r[2] or '-'}")
    db.close(); pause()


def _select_product(cur, kw):
    cur.execute(
        "SELECT barcode, name FROM Product WHERE name LIKE ? ORDER BY name",
        (f'%{kw}%',)
    )
    rows = cur.fetchall()
    if not rows:
        print('  No products found.')
        return None
    print(f"\n  {'#':>3} {'Product':<32} {'Barcode'}")
    sep()
    for i, r in enumerate(rows, 1):
        print(f"  {i:>3} {wl(r[1],32)} {r[0]}")
    sel = input('\n  Select product # > ').strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(rows)):
        return None
    return rows[int(sel) - 1][0]


def dba_pt_add():
    kw = input('Product name keyword > ').strip()
    if not kw: return
    db = conn(); cur = db.cursor()
    barcode = _select_product(cur, kw)
    if not barcode:
        db.close(); return

    type_name = input('  Type name > ').strip()
    if not type_name:
        db.close(); return

    cur.execute(
        "SELECT id FROM ProductType WHERE productBarcode = ? AND name = ?",
        (barcode, type_name)
    )
    if cur.fetchone():
        print('  Type already assigned to this product.')
        db.close(); pause(); return

    cur.execute(
        "INSERT INTO ProductType(name, productBarcode) VALUES (?, ?)",
        (type_name, barcode)
    )
    db.commit()
    print(f"  Added type '{type_name}'.")
    db.close(); pause()


def dba_pt_remove():
    kw = input('Product name keyword > ').strip()
    if not kw: return
    db = conn(); cur = db.cursor()
    barcode = _select_product(cur, kw)
    if not barcode:
        db.close(); return

    cur.execute(
        "SELECT id, name FROM ProductType WHERE productBarcode = ? ORDER BY name",
        (barcode,)
    )
    types = cur.fetchall()
    if not types:
        print('  No types assigned to this product.')
        db.close(); pause(); return

    print(f"\n  {'#':>3} {'Type Name'}")
    sep(30)
    for i, t in enumerate(types, 1):
        print(f"  {i:>3} {t[1]}")
    sel = input('\n  Select type # to remove > ').strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(types)):
        db.close(); return

    cur.execute("DELETE FROM ProductType WHERE id = ?", (types[int(sel) - 1][0],))
    db.commit()
    print('  Type removed.')
    db.close(); pause()
