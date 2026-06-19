from utils import conn, wl, header, sep, pause


def olap_menu():
    while True:
        header('OLAP Analytics')
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
    cur.execute("""
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


# Category analysis uses ProductType leaf rows (productBarcode IS NOT NULL).
# Hierarchy: leaf → Level1 → root, traversable via parentId (recursive CTE).
# Products with multiple leaf types are counted in each category.
def olap_category():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT COALESCE(pt.name, 'Uncategorized') AS cat,
               COUNT(DISTINCT s.id)            AS txn,
               SUM(si.quantity)                AS qty,
               SUM(si.quantity * si.unitPrice) AS revenue
        FROM SalesItem si
        JOIN Product p ON si.productBarcode = p.barcode
        JOIN Sales   s ON si.salesId = s.id
        LEFT JOIN ProductType pt ON pt.productBarcode = p.barcode
        GROUP BY cat ORDER BY revenue DESC
    """)
    rows = cur.fetchall()
    header('Category Revenue  (by Product Type)')
    print(f"  {'Category':<28} {'Txns':>6} {'Units':>8} {'Revenue':>14}  {'Share':>6}")
    sep()
    total = sum(r[3] for r in rows)
    for r in rows:
        pct = r[3] / total * 100 if total else 0
        print(f"  {wl(r[0],28)} {r[1]:>6} {r[2]:>8} {r[3]:>14,}  {pct:5.1f}%")
    db.close(); pause()


def olap_region_category():
    db = conn(); cur = db.cursor()
    cur.execute("""
        SELECT st.region,
               COALESCE(pt.name, 'Uncategorized') AS cat,
               SUM(si.quantity * si.unitPrice)     AS revenue
        FROM SalesItem si
        JOIN Product p ON si.productBarcode = p.barcode
        JOIN Sales   s ON si.salesId = s.id
        JOIN Store  st ON s.storeId = st.id
        LEFT JOIN ProductType pt ON pt.productBarcode = p.barcode
        GROUP BY st.region, cat
        ORDER BY st.region, revenue DESC
    """)
    rows = cur.fetchall()
    header('Category Sales by Region  (by Product Type)')
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
    cur.execute("""
        SELECT SUBSTR(s.saleDate,1,7)           AS m,
               COALESCE(pt.name, 'Uncategorized') AS cat,
               SUM(si.quantity * si.unitPrice)  AS revenue
        FROM SalesItem si
        JOIN Product p ON si.productBarcode = p.barcode
        JOIN Sales   s ON si.salesId = s.id
        LEFT JOIN ProductType pt ON pt.productBarcode = p.barcode
        GROUP BY m, cat
        ORDER BY m, revenue DESC
    """)
    rows = cur.fetchall()
    header('Monthly Category Trend  (by Product Type)')
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
