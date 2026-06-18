import sqlite3

conn = sqlite3.connect("database/emart.db")
cursor = conn.cursor()

# --- Distributor 조회 ---
print("=== [Distributor 테이블 조회] ===")
cursor.execute("SELECT * FROM Distributor")
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row[0]} | 매칭 유통사: {row[1]} | 웹사이트: {row[2]}")

print("\n" + "="*50 + "\n")

# --- Supplier 조회 ---
print("=== [Supplier 테이블 조회] ===")
cursor.execute("SELECT * FROM Supplier")
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row[0]} | 공급업체명: {row[1]} | 연락처: {row[2]}")

print("\n" + "="*50 + "\n")


# ==========================================
# 3. Brand 테이블 조회 (공급업체명 JOIN)
# ==========================================
print("=== [Brand 테이블 조회] ===")
cursor.execute("""
    SELECT B.id, B.name, S.name 
    FROM Brand B
    JOIN Supplier S ON B.supplierId = S.id
""")
rows = cursor.fetchall()
for row in rows:
    print(f"브랜드 ID: {row[0]:<2} | 브랜드명: {row[1]:<10} | 소속 공급업체: {row[2]}")

print("\n" + "="*50 + "\n")


# ==========================================
# 4. Product 테이블 조회 (브랜드명 JOIN)
# ==========================================
print("=== [Product 테이블 조회 (상위 15개만 표시)] ===")
cursor.execute("""
    SELECT P.barcode, P.name, P.specification, P.wrap, P.price, B.name
    FROM Product P
    LEFT JOIN Brand B ON P.brandId = B.id
    LIMIT 15
""")
rows = cursor.fetchall()
for row in rows:
    print(f"바코드: {row[0]} | 상품명: {row[1]:<15} | 규격: {row[2]:<6} | 포장: {row[3]:<4} | 가격: {row[4]:>5}원 | 브랜드: {row[5]}")

# 전체 상품 개수 출력하여 검증
cursor.execute("SELECT COUNT(*) FROM Product")
total_count = cursor.fetchone()[0]
print(f"\n 등록된 총 상품 개수: {total_count}개")


# ==========================================
# 5. Store 테이블 조회
# ==========================================

print("\n" + "="*50 + "\n")
print("=== [Store 테이블 조회] ===")

cursor.execute("""
    SELECT
        S.id,
        S.name,
        S.address,
        S.region,
        S.openHour,
        S.closeHour,
        D.name
    FROM Store S
    JOIN Distributor D
        ON S.distributorId = D.id
""")

rows = cursor.fetchall()

for row in rows:
    print(
        f"매장 ID: {row[0]} | "
        f"매장명: {row[1]} | "
        f"지역: {row[3]} | "
        f"영업시간: {row[4]}~{row[5]} | "
        f"유통사: {row[6]}"
    )

cursor.execute("SELECT COUNT(*) FROM Store")
count = cursor.fetchone()[0]

print(f"\n등록된 총 매장 수: {count}개")


# ==========================================
# 6. Customer 테이블 조회
# ==========================================

print("\n" + "="*50 + "\n")
print("=== [Customer 테이블 조회] ===")

cursor.execute("""
    SELECT
        C.id,
        C.name,
        C.phone,
        C.birthday,
        C.email,
        D.name
    FROM Customer C
    JOIN Distributor D
        ON C.distributorId = D.id
    LIMIT 15
""")

rows = cursor.fetchall()

for row in rows:
    birthday = row[3] if row[3] else "미입력"

    print(
        f"고객 ID: {row[0]:<2} | "
        f"이름: {row[1]:<6} | "
        f"전화번호: {row[2]} | "
        f"생년월일: {birthday:<10} | "
        f"이메일: {row[4]:<25} | "
        f"유통사: {row[5]}"
    )

cursor.execute("SELECT COUNT(*) FROM Customer")
count = cursor.fetchone()[0]

print(f"\n등록된 총 고객 수: {count}명")

# ==========================================
# 7. Stocks 테이블 조회
# ==========================================

print("\n" + "="*50 + "\n")
print("=== [Stocks 테이블 조회 (상위 20개)] ===")

cursor.execute("""
SELECT
    S.storeId,
    ST.name,
    P.name,
    S.quantity,
    S.reorderPoint
FROM Stocks S
JOIN Store ST
    ON S.storeId = ST.id
JOIN Product P
    ON S.productBarcode = P.barcode
LIMIT 20
""")

rows = cursor.fetchall()

for row in rows:
    print(
        f"매장ID:{row[0]} | "
        f"매장:{row[1]:<10} | "
        f"상품:{row[2]:<20} | "
        f"재고:{row[3]:>3} | "
        f"재주문기준:{row[4]}"
    )

cursor.execute("SELECT COUNT(*) FROM Stocks")
count = cursor.fetchone()[0]

print(f"\n등록된 재고 레코드 수: {count}")

# ==========================================
# 8. Sales 테이블 조회
# ==========================================

print("\n" + "="*50 + "\n")
print("=== [Sales 테이블 조회 (상위 10개)] ===")

cursor.execute("""
SELECT
    S.id,
    C.name,
    ST.name,
    S.saleDate,
    S.totalPrice
FROM Sales S
JOIN Customer C
    ON S.customerId = C.id
JOIN Store ST
    ON S.storeId = ST.id
LIMIT 10
""")

for row in cursor.fetchall():
    print(
        f"판매ID:{row[0]} | "
        f"고객:{row[1]} | "
        f"매장:{row[2]} | "
        f"총액:{row[4]}원"
    )


# ==========================================
# 9. SalesItem 테이블 조회
# ==========================================

print("\n" + "="*50 + "\n")
print("=== [SalesItem 테이블 조회 (상위 20개)] ===")

cursor.execute("""
SELECT
    SI.salesId,
    P.name,
    SI.quantity,
    SI.unitPrice
FROM SalesItem SI
JOIN Product P
    ON SI.productBarcode = P.barcode
LIMIT 20
""")

for row in cursor.fetchall():
    print(
        f"판매ID:{row[0]} | "
        f"상품:{row[1]:<20} | "
        f"수량:{row[2]} | "
        f"단가:{row[3]}원"
    )

cursor.execute("SELECT COUNT(*) FROM SalesItem")
count = cursor.fetchone()[0]

print(f"\n등록된 SalesItem 수: {count}")

# ==========================================
# 10. Order 테이블 조회
# ==========================================
print("\n" + "="*50 + "\n")
print("=== [OrderTable 조회] ===")

cursor.execute("""
SELECT
    O.id,
    O.orderDate,
    O.status,
    S.name,
    ST.name
FROM OrderTable O
JOIN Supplier S
    ON O.supplierId = S.id
JOIN Store ST
    ON O.storeId = ST.id
LIMIT 20
""")

for row in cursor.fetchall():
    print(
        f"발주ID:{row[0]} | "
        f"상태:{row[2]} | "
        f"공급업체:{row[3]} | "
        f"매장:{row[4]}"
    )

cursor.execute("SELECT COUNT(*) FROM OrderTable")
print(f"\n총 발주 건수: {cursor.fetchone()[0]}")

# ==========================================
# 11. OrderItem 테이블 조회
# ==========================================
print("\n" + "="*50 + "\n")
print("=== [OrderItem 조회] ===")

cursor.execute("""
SELECT
    OI.orderId,
    P.name,
    OI.quantity,
    OI.deliveredQuantity,
    OI.deliveredAt
FROM OrderItem OI
JOIN Product P
    ON OI.productBarcode = P.barcode
LIMIT 20
""")

for row in cursor.fetchall():

    delivered_at = (
        row[4]
        if row[4]
        else "미납품"
    )

    print(
        f"발주ID:{row[0]} | "
        f"상품:{row[1]:<20} | "
        f"발주:{row[2]}개 | "
        f"납품:{row[3]}개 | "
        f"납품시각:{delivered_at}"
    )

cursor.execute("SELECT COUNT(*) FROM OrderItem")
print(f"\n총 발주상품 건수: {cursor.fetchone()[0]}")

conn.close()