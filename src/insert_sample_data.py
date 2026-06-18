import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("database/emart.db")
cursor = conn.cursor()

# 외래 키 제약조건 활성화
cursor.execute("PRAGMA foreign_keys = ON;")

# 1. Distributor 데이터 삽입
cursor.execute("""
INSERT INTO Distributor(name, website)
VALUES (?, ?)
""", ("Emart", "https://www.emart.com"))
distributor_id = cursor.lastrowid # 방금 넣은 이마트의 ID (1)

# 2. Supplier 데이터 삽입
suppliers = [
    ("CJ제일제당", "02-1234-1111"),
    ("농심", "02-1234-2222"),
    ("오뚜기", "02-1234-3333"),
    ("롯데웰푸드", "02-1234-4444"),
    ("코카콜라음료", "02-1234-5555")
]
cursor.executemany("""
INSERT INTO Supplier(name, contact)
VALUES (?, ?)
""", suppliers)

# 3. brands 데이터 삽입
brands = [
    ("백설", 1),          # CJ제일제당
    ("햇반", 1),

    ("신라면", 2),        # 농심
    ("새우깡", 2),

    ("진라면", 3),        # 오뚜기
    ("오뚜기카레", 3),

    ("빼빼로", 4),        # 롯데웰푸드
    ("칸쵸", 4),

    ("코카콜라", 5),      # 코카콜라음료
    ("스프라이트", 5)
]

cursor.executemany("""
INSERT INTO Brand(name, supplierId)
VALUES (?, ?)
""", brands)

# 4. Product 데이터 삽입
products = [
    # 백설 (brandId = 1)
    ("880100000001", "백설 설탕 1kg", "1kg", "봉지", 3500, 1),
    ("880100000002", "백설 밀가루 1kg", "1kg", "봉지", 2800, 1),
    ("880100000003", "백설 부침가루", "500g", "봉지", 2500, 1),

    # 햇반 (brandId = 2)
    ("880100000004", "햇반 210g", "210g", "플라스틱", 1800, 2),
    ("880100000005", "햇반 흑미밥", "210g", "플라스틱", 2200, 2),

    # 신라면 (brandId = 3)
    ("880200000001", "신라면", "120g", "비닐", 1000, 3),
    ("880200000002", "신라면 5입", "600g", "비닐", 4500, 3),
    ("880200000003", "신라면 블랙", "130g", "비닐", 1600, 3),

    # 새우깡 (brandId = 4)
    ("880200000004", "새우깡", "90g", "비닐", 1500, 4),
    ("880200000005", "매운새우깡", "90g", "비닐", 1600, 4),

    # 진라면 (brandId = 5)
    ("880300000001", "진라면 매운맛", "120g", "비닐", 950, 5),
    ("880300000002", "진라면 순한맛", "120g", "비닐", 950, 5),
    ("880300000003", "진라면 매운맛 5입", "600g", "비닐", 4300, 5),

    # 오뚜기카레 (brandId = 6)
    ("880300000004", "오뚜기카레 순한맛", "100g", "상자", 2800, 6),
    ("880300000005", "오뚜기카레 매운맛", "100g", "상자", 2800, 6),

    # 빼빼로 (brandId = 7)
    ("880400000001", "빼빼로 오리지널", "54g", "상자", 1800, 7),
    ("880400000002", "아몬드 빼빼로", "37g", "상자", 2000, 7),
    ("880400000003", "누드 빼빼로", "50g", "상자", 2200, 7),

    # 칸쵸 (brandId = 8)
    ("880400000004", "칸쵸 초코", "54g", "상자", 1700, 8),
    ("880400000005", "칸쵸 딸기", "54g", "상자", 1700, 8),

    # 코카콜라 (brandId = 9)
    ("880500000001", "코카콜라 250ml", "250ml", "캔", 1500, 9),
    ("880500000002", "코카콜라 500ml", "500ml", "PET", 2200, 9),
    ("880500000003", "코카콜라 1.5L", "1.5L", "PET", 3800, 9),

    # 스프라이트 (brandId = 10)
    ("880500000004", "스프라이트 250ml", "250ml", "캔", 1500, 10),
    ("880500000005", "스프라이트 500ml", "500ml", "PET", 2200, 10),
    ("880500000006", "스프라이트 1.5L", "1.5L", "PET", 3800, 10)
]

cursor.executemany("""
INSERT INTO Product(
    barcode,
    name,
    specification,
    wrap,
    price,
    brandId
)
VALUES (?, ?, ?, ?, ?, ?)
""", products)

# 5. Store 데이터 삽입

stores = [
    (
        "이마트 강남점",
        "서울특별시 강남구 삼성로 123",
        "서울",
        "10:00",
        "23:00",
        distributor_id
    ),
    (
        "이마트 신촌점",
        "서울특별시 서대문구 신촌로 45",
        "서울",
        "10:00",
        "23:00",
        distributor_id
    ),
    (
        "이마트 목동점",
        "서울특별시 양천구 목동동로 257",
        "서울",
        "10:00",
        "23:00",
        distributor_id
    ),
    (
        "이마트 양평점",
        "서울특별시 영등포구 선유로 138",
        "서울",
        "10:00",
        "23:00",
        distributor_id
    ),
    (
        "이마트 노원점",
        "서울특별시 노원구 동일로 1414",
        "서울",
        "10:00",
        "23:00",
        distributor_id
    )
]

cursor.executemany("""
INSERT INTO Store(
    name,
    address,
    region,
    openHour,
    closeHour,
    distributorId
)
VALUES (?, ?, ?, ?, ?, ?)
""", stores)

# 6. Customer 데이터 삽입

customers = [
    ("김민지", "010-1111-1111", "2003-03-15", "서울 강남구", "minji1@email.com", "pw1234", distributor_id),
    ("이서연", "010-1111-2222", "2002-07-21", "서울 서대문구", "seoyeon@email.com", "pw1234", distributor_id),
    ("박지훈", "010-1111-3333", "2001-05-11", "서울 양천구", "jihun@email.com", "pw1234", distributor_id),
    ("최현우", "010-1111-4444", "2000-09-03", "서울 노원구", "hyunwoo@email.com", "pw1234", distributor_id),
    ("정예린", "010-1111-5555", "2002-01-19", "서울 영등포구", "yerin@email.com", "pw1234", distributor_id),

    ("한지민", "010-2222-1111", None, "서울 강남구", "jimin@email.com", "pw1234", distributor_id),
    ("김도윤", "010-2222-2222", "1999-04-10", "서울 서초구", "doyoon@email.com", "pw1234", distributor_id),
    ("윤채원", "010-2222-3333", None, "서울 마포구", "chaewon@email.com", "pw1234", distributor_id),
    ("오준혁", "010-2222-4444", "2001-08-08", "서울 강동구", "junhyuk@email.com", "pw1234", distributor_id),
    ("장서진", "010-2222-5555", "2000-11-25", "서울 송파구", "seojin@email.com", "pw1234", distributor_id),

    ("김하늘", "010-3333-1111", None, "서울 은평구", "haneul@email.com", "pw1234", distributor_id),
    ("이지우", "010-3333-2222", "2003-06-14", "서울 중구", "jiwoo@email.com", "pw1234", distributor_id),
    ("박서준", "010-3333-3333", "1998-12-01", "서울 성북구", "seojun@email.com", "pw1234", distributor_id),
    ("최수빈", "010-3333-4444", None, "서울 동작구", "subin@email.com", "pw1234", distributor_id),
    ("정우성", "010-3333-5555", "1997-02-28", "서울 광진구", "woosung@email.com", "pw1234", distributor_id)
]

cursor.executemany("""
INSERT INTO Customer(
    name,
    phone,
    birthday,
    address,
    email,
    password,
    distributorId
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", customers)

import random


# 7. Stocks 데이터 생성

# 매장 ID 조회
cursor.execute("SELECT id FROM Store")
store_ids = [row[0] for row in cursor.fetchall()]

# 상품 바코드 조회
cursor.execute("SELECT barcode FROM Product")
product_barcodes = [row[0] for row in cursor.fetchall()]

stocks = []

for store_id in store_ids:
    for barcode in product_barcodes:

        # 현재 재고 (0~120개)
        quantity = random.randint(0, 120)

        # 재주문 기준 재고
        reorder_point = random.choice([10, 15, 20])

        stocks.append(
            (
                store_id,
                barcode,
                quantity,
                reorder_point
            )
        )

cursor.executemany("""
INSERT INTO Stocks(
    storeId,
    productBarcode,
    quantity,
    reorderPoint
)
VALUES (?, ?, ?, ?)
""", stocks)

print(f"Stocks 데이터 {len(stocks)}건 생성 완료")


# 8. Sales 데이터 생성

sales_count = 100

sales = []

for _ in range(sales_count):

    customer_id = random.randint(1, 15)
    store_id = random.randint(1, 5)

    random_days = random.randint(0, 180)

    sale_date = (
        datetime.now() - timedelta(days=random_days)
    ).strftime("%Y-%m-%d %H:%M:%S")

    total_price = 0  # 나중에 SalesItem 생성 후 업데이트

    sales.append(
        (
            sale_date,
            total_price,
            customer_id,
            store_id
        )
    )

cursor.executemany("""
INSERT INTO Sales(
    saleDate,
    totalPrice,
    customerId,
    storeId
)
VALUES (?, ?, ?, ?)
""", sales)

print(f"Sales 데이터 {sales_count}건 생성 완료")


# 9. SalesItem 데이터 생성

cursor.execute("""
SELECT barcode, price
FROM Product
""")

products = cursor.fetchall()

cursor.execute("""
SELECT id
FROM Sales
""")

sale_ids = [row[0] for row in cursor.fetchall()]

sales_items = []

for sale_id in sale_ids:

    item_count = random.randint(1, 5)

    selected_products = random.sample(
        products,
        item_count
    )

    sale_total = 0

    for barcode, price in selected_products:

        quantity = random.randint(1, 4)

        sales_items.append(
            (
                sale_id,
                barcode,
                quantity,
                price
            )
        )

        sale_total += quantity * price

    cursor.execute("""
    UPDATE Sales
    SET totalPrice = ?
    WHERE id = ?
    """, (sale_total, sale_id))

cursor.executemany("""
INSERT INTO SalesItem(
    salesId,
    productBarcode,
    quantity,
    unitPrice
)
VALUES (?, ?, ?, ?)
""", sales_items)

print(
    f"SalesItem 데이터 {len(sales_items)}건 생성 완료"
)


# 10. OrderTable / OrderItem 자동 생성

from datetime import datetime

# 재주문 대상 조회
cursor.execute("""
SELECT
    ST.storeId,
    ST.productBarcode,
    P.brandId,
    B.supplierId
FROM Stocks ST
JOIN Product P
    ON ST.productBarcode = P.barcode
JOIN Brand B
    ON P.brandId = B.id
WHERE ST.quantity <= ST.reorderPoint
""")

reorder_targets = cursor.fetchall()

order_count = 0
order_item_count = 0

for target in reorder_targets:

    store_id = target[0]
    barcode = target[1]
    supplier_id = target[3]

    # OrderTable 생성
    cursor.execute("""
    INSERT INTO OrderTable(
        orderDate,
        status,
        supplierId,
        storeId
    )
    VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "PENDING",
        supplier_id,
        store_id
    ))

    order_id = cursor.lastrowid

    order_count += 1

    # OrderItem 생성
    cursor.execute("""
    INSERT INTO OrderItem(
        orderId,
        productBarcode,
        quantity,
        deliveredQuantity,
        deliveredAt
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        order_id,
        barcode,
        50,      # 기본 발주량
        0,
        None
    ))

    order_item_count += 1

print(f"OrderTable 데이터 {order_count}건 생성 완료")
print(f"OrderItem 데이터 {order_item_count}건 생성 완료")

conn.commit()
conn.close()

print("Data inserted")