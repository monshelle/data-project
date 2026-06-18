import sqlite3
import os

# 데이터베이스 폴더가 없을 경우 생성
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect("database/emart.db")
cursor = conn.cursor()

# SQLite에서 외래 키(Foreign Key) 제약조건 활성화
cursor.execute("PRAGMA foreign_keys = ON;")

# 1. Distributor 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS Distributor(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    website TEXT
)
""")

# 2. Supplier 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS Supplier(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT
)
""")

# 3. Brand 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS Brand(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    supplierId INTEGER NOT NULL,
    FOREIGN KEY (supplierId) REFERENCES Supplier(id)
);
""")

# 4. Product 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS Product(
    barcode TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    specification TEXT,
    wrap TEXT,
    price INTEGER NOT NULL,
    brandId INTEGER,
    FOREIGN KEY (brandId) REFERENCES Brand(id)
);
""")

# 5. ProductType 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS ProductType(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    productBarcode TEXT,
    FOREIGN KEY (productBarcode) REFERENCES Product(barcode)
);
""")

# 6. Store 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS Store(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    region TEXT,
    openHour TEXT,
    closeHour TEXT,
    distributorId INTEGER,
    FOREIGN KEY (distributorId) REFERENCES Distributor(id)
);
""")

# 7. Customer 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customer(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    birthday TEXT NULL, -- 제약조건 2: NULL 허용 명시
    address TEXT,
    email TEXT UNIQUE,  -- 제약조건 1: UNIQUE 설정
    password TEXT NOT NULL,
    distributorId INTEGER,
    FOREIGN KEY (distributorId) REFERENCES Distributor(id)
);
""")

# 8. Stocks 테이블 (복합 기본키)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Stocks(
    storeId INTEGER,
    productBarcode TEXT,
    quantity INTEGER NOT NULL DEFAULT 0,
    reorderPoint INTEGER NOT NULL DEFAULT 10,
    PRIMARY KEY(storeId, productBarcode),
    FOREIGN KEY (storeId) REFERENCES Store(id),
    FOREIGN KEY (productBarcode) REFERENCES Product(barcode),
    CONSTRAINT chk_stocks_quantity CHECK (quantity >= 0),        -- 제약조건 3
    CONSTRAINT chk_stocks_reorder CHECK (reorderPoint > 0)       -- 제약조건 4
);
""")

# 9. Sales 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS Sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    saleDate TEXT NOT NULL,
    totalPrice INTEGER NOT NULL,
    customerId INTEGER,
    storeId INTEGER,
    FOREIGN KEY (customerId) REFERENCES Customer(id),
    FOREIGN KEY (storeId) REFERENCES Store(id),
    CONSTRAINT chk_sales_total_price CHECK (totalPrice >= 0)      -- 제약조건 5
);
""")

# 10. SalesItem 테이블 (복합 기본키)
cursor.execute("""
CREATE TABLE IF NOT EXISTS SalesItem(
    salesId INTEGER,
    productBarcode TEXT,
    quantity INTEGER NOT NULL,
    unitPrice INTEGER NOT NULL,
    PRIMARY KEY(salesId, productBarcode),
    FOREIGN KEY (salesId) REFERENCES Sales(id),
    FOREIGN KEY (productBarcode) REFERENCES Product(barcode),
    CONSTRAINT chk_salesitem_quantity CHECK (quantity > 0)       -- 제약조건 6
);
""")

# 11. Order 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS OrderTable( -- SQLite 예약어 무충돌을 위해 OrderTable로 명명 권장
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orderDate TEXT NOT NULL,
    status TEXT NOT NULL,
    supplierId INTEGER,
    storeId INTEGER,
    FOREIGN KEY (supplierId) REFERENCES Supplier(id),
    FOREIGN KEY (storeId) REFERENCES Store(id),
    -- 제약조건 8: status CHECK 제약조건
    CONSTRAINT chk_order_status CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED'))
);
""")

# 12. OrderItem 테이블 (복합 기본키)
cursor.execute("""
CREATE TABLE IF NOT EXISTS OrderItem(
    orderId INTEGER,
    productBarcode TEXT,
    quantity INTEGER NOT NULL,
    deliveredQuantity INTEGER DEFAULT 0,
    deliveredAt TEXT,
    PRIMARY KEY(orderId, productBarcode),
    FOREIGN KEY (orderId) REFERENCES OrderTable(id),
    FOREIGN KEY (productBarcode) REFERENCES Product(barcode),
    CONSTRAINT chk_orderitem_quantity CHECK (quantity > 0)       -- 제약조건 7
);
""")

conn.commit()
conn.close()

print("Table created")