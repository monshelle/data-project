import sqlite3
from datetime import datetime
from utils import conn, wl, header, sep, pause


def ensure_customer_tables():
    db = conn(); cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Cart(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customerId INTEGER NOT NULL,
            createdAt TEXT NOT NULL,
            FOREIGN KEY(customerId) REFERENCES Customer(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS CartItem(
            cartId INTEGER NOT NULL,
            productBarcode TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            PRIMARY KEY(cartId, productBarcode),
            FOREIGN KEY(cartId) REFERENCES Cart(id),
            FOREIGN KEY(productBarcode) REFERENCES Product(barcode),
            CONSTRAINT chk_cartitem_quantity CHECK(quantity > 0)
        )
    """)
    db.commit(); db.close()


def _get_or_create_cart(cur, customer_id):
    cur.execute(
        'SELECT id FROM Cart WHERE customerId = ? ORDER BY id DESC LIMIT 1',
        (customer_id,)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        'INSERT INTO Cart(customerId, createdAt) VALUES (?, ?)',
        (customer_id, created_at)
    )
    return cur.lastrowid


def _get_cart_items(cur, customer_id):
    cur.execute("""
        SELECT c.id, ci.productBarcode, p.name, ci.quantity, p.price,
               ci.quantity * p.price AS line_total
        FROM Cart c
        JOIN CartItem ci ON ci.cartId = c.id
        JOIN Product p ON p.barcode = ci.productBarcode
        WHERE c.customerId = ?
        ORDER BY p.name
    """, (customer_id,))
    return cur.fetchall()


def show_cart_items(customer_id):
    db = conn(); cur = db.cursor()
    rows = _get_cart_items(cur, customer_id)
    header('Cart')
    if not rows:
        print('  Cart is empty.')
        db.close(); pause(); return

    print(f"  {'Barcode':<16} {'Product':<28} {'Qty':>4} {'Price':>10} {'Total':>12}")
    sep()
    grand_total = 0
    for _, barcode, name, qty, price, line_total in rows:
        print(f"  {barcode:<16} {wl(name,28)} {qty:>4} {price:>10,} {line_total:>12,}")
        grand_total += line_total
    sep()
    print(f"  {'Grand Total':<50} {grand_total:>12,}")
    db.close(); pause()


def add_product_to_cart(customer_id, barcode, quantity):
    db = conn(); cur = db.cursor()
    cur.execute('SELECT barcode, name, price FROM Product WHERE barcode = ?', (barcode,))
    product = cur.fetchone()
    if not product:
        print('  Invalid product barcode.')
        db.close(); pause(); return

    cart_id = _get_or_create_cart(cur, customer_id)
    cur.execute(
        'SELECT quantity FROM CartItem WHERE cartId = ? AND productBarcode = ?',
        (cart_id, barcode)
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            'UPDATE CartItem SET quantity = quantity + ? WHERE cartId = ? AND productBarcode = ?',
            (quantity, cart_id, barcode)
        )
    else:
        cur.execute(
            'INSERT INTO CartItem(cartId, productBarcode, quantity) VALUES (?, ?, ?)',
            (cart_id, barcode, quantity)
        )
    db.commit()
    print(f"  Added to cart: {product[1]} x {quantity}")
    db.close(); pause()


def buy_cart(customer_id):
    db = conn(); cur = db.cursor()
    items = _get_cart_items(cur, customer_id)
    header('Buy Cart')
    if not items:
        print('  Cart is empty.')
        db.close(); pause(); return

    cur.execute('SELECT id, name, region FROM Store ORDER BY id')
    stores = cur.fetchall()
    print('  Select store to buy from:')
    for store in stores:
        print(f"    {store[0]}. {store[1]} ({store[2]})")
    store_id_raw = input('\n  Store ID > ').strip()
    if not store_id_raw.isdigit():
        db.close(); return
    store_id = int(store_id_raw)
    cur.execute('SELECT name FROM Store WHERE id = ?', (store_id,))
    store = cur.fetchone()
    if not store:
        print('  Invalid store.')
        db.close(); pause(); return

    shortages = []
    for _, barcode, name, qty, _, _ in items:
        cur.execute(
            'SELECT quantity FROM Stocks WHERE storeId = ? AND productBarcode = ?',
            (store_id, barcode)
        )
        row = cur.fetchone()
        stock_qty = row[0] if row else 0
        if stock_qty < qty:
            shortages.append((name, qty, stock_qty))

    if shortages:
        print('\n  Not enough stock for:')
        for name, qty, stock_qty in shortages:
            print(f'    {wl(name,28)} need {qty}, have {stock_qty}')
        db.close(); pause(); return

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_price = sum(line_total for *_, line_total in items)
    cur.execute(
        'INSERT INTO Sales(saleDate, totalPrice, customerId, storeId) VALUES (?, ?, ?, ?)',
        (now, total_price, customer_id, store_id)
    )
    sale_id = cur.lastrowid
    for _, barcode, _, qty, price, _ in items:
        cur.execute(
            'INSERT INTO SalesItem(salesId, productBarcode, quantity, unitPrice) VALUES (?, ?, ?, ?)',
            (sale_id, barcode, qty, price)
        )
        cur.execute(
            'UPDATE Stocks SET quantity = quantity - ? WHERE storeId = ? AND productBarcode = ?',
            (qty, store_id, barcode)
        )

    cur.execute('DELETE FROM CartItem WHERE cartId IN (SELECT id FROM Cart WHERE customerId = ?)', (customer_id,))
    db.commit()
    print(f'  Purchase completed. Sale #{sale_id}, total {total_price:,}')
    db.close(); pause()


def signup_customer():
    header('Customer Sign Up')
    name = input('  Name > ').strip()
    email = input('  Email > ').strip()
    password = input('  Password > ').strip()
    phone = input('  Phone (Enter to skip) > ').strip() or None
    birthday = input('  Birthday YYYY-MM-DD (Enter to skip) > ').strip() or None
    address = input('  Address (Enter to skip) > ').strip() or None

    if not name or not email or not password:
        print('  Name, email, and password are required.')
        pause(); return

    db = conn(); cur = db.cursor()
    try:
        cur.execute("""
            INSERT INTO Customer(name, phone, birthday, address, email, password, distributorId)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (name, phone, birthday, address, email, password))
        db.commit()
        print(f'  Sign up complete. Customer ID: {cur.lastrowid}')
    except sqlite3.IntegrityError:
        print('  Email already exists.')
    finally:
        db.close(); pause()


def login_customer():
    header('Customer Log In')
    email = input('  Email > ').strip()
    if not email:
        return None
    password = input('  Password > ').strip()
    if not password:
        return None

    db = conn(); cur = db.cursor()
    cur.execute('SELECT id, name, email FROM Customer WHERE email = ? AND password = ?', (email, password))
    customer = cur.fetchone()
    db.close()
    if not customer:
        print('  Invalid email or password.')
        pause(); return None
    return {'id': customer[0], 'name': customer[1], 'email': customer[2]}


def consumer_search(customer_id=None):
    kw = input('Search keyword > ').strip()
    if not kw:
        return
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
        print(f"  {'#':>3} {'Product':<28} {'Spec':<8} {'Pack':<6} {'Price':>8}")
        sep()
        for i, r in enumerate(rows, 1):
            print(f"  {i:>3} {wl(r[1],28)} {wl(r[2] or '-',8)} {wl(r[3] or '-',6)} {r[4]:>8,}")
        if customer_id is not None:
            sel = input('\n  Add item # to cart (Enter to skip) > ').strip()
            if sel.isdigit() and 1 <= int(sel) <= len(rows):
                barcode = rows[int(sel) - 1][0]
                qty_raw = input('  Quantity > ').strip()
                if qty_raw.isdigit() and int(qty_raw) > 0:
                    add_product_to_cart(customer_id, barcode, int(qty_raw))
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


def consumer_history(customer_id=None):
    db = conn(); cur = db.cursor()
    if customer_id is None:
        cur.execute('SELECT id, name FROM Customer ORDER BY id')
        customers = cur.fetchall()
        print('\n  Customer List:')
        for c in customers:
            print(f"    {c[0]:>3}. {c[1]}")
        cid = input('\n  Customer ID > ').strip()
        if not cid.isdigit():
            db.close(); return
        customer_id = int(cid)
    else:
        cid = str(customer_id)
    cur.execute("""
        SELECT s.id, s.saleDate, st.name, p.name,
               si.quantity, si.unitPrice, si.quantity * si.unitPrice
        FROM Sales s
        JOIN Store st ON s.storeId = st.id
        JOIN SalesItem si ON si.salesId = s.id
        JOIN Product p ON si.productBarcode = p.barcode
        WHERE s.customerId = ?
        ORDER BY s.saleDate DESC, s.id
    """, (customer_id,))
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


def customer_cart_menu(customer_id):
    while True:
        header('Cart')
        print('  1. View Cart')
        print('  2. Buy')
        print('  0. Back')
        c = input('\nSelect > ').strip()
        if c == '0':
            break
        elif c == '1':
            show_cart_items(customer_id)
        elif c == '2':
            buy_cart(customer_id)


def customer_session_menu(customer):
    while True:
        header(f'Customer: {customer["name"]}')
        print('  1. Search Product')
        print('  2. Cart')
        print('  3. My Purchase History')
        print('  4. Store Info')
        print('  0. Log Out')
        c = input('\nSelect > ').strip()
        if c == '0':
            break
        elif c == '1':
            consumer_search(customer['id'])
        elif c == '2':
            customer_cart_menu(customer['id'])
        elif c == '3':
            consumer_history(customer['id'])
        elif c == '4':
            consumer_store_info()


def consumer_menu():
    while True:
        header('Customer Interface')
        print('  1. Sign Up')
        print('  2. Log In')
        print('  0. Back')
        c = input('\nSelect > ').strip()
        if c == '0':
            break
        elif c == '1':
            signup_customer()
        elif c == '2':
            customer = login_customer()
            if customer:
                customer_session_menu(customer)
