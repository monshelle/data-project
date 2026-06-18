import sqlite3

conn = sqlite3.connect("database/emart.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

# Cart 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS Cart(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customerId INTEGER NOT NULL,
    createdAt TEXT NOT NULL,

    FOREIGN KEY(customerId)
        REFERENCES Customer(id)
);
""")

# CartItem 테이블
cursor.execute("""
CREATE TABLE IF NOT EXISTS CartItem(
    cartId INTEGER NOT NULL,
    productBarcode TEXT NOT NULL,
    quantity INTEGER NOT NULL,

    PRIMARY KEY(cartId, productBarcode),

    FOREIGN KEY(cartId)
        REFERENCES Cart(id),

    FOREIGN KEY(productBarcode)
        REFERENCES Product(barcode),

    CHECK(quantity > 0)
);
""")

conn.commit()
conn.close()

print("Cart, CartItem 테이블 생성 완료")