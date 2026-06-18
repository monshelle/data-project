from db_connection import get_connection
from datetime import datetime

def oltp_menu():

    while True:

        print("\n")
        print("=====================================")
        print("        DISTRIBUTOR - OLTP")
        print("=====================================")

        print("[1] Process New Sale")
        print("[2] Cancel Sale")
        print("[3] Check Stock")
        print("[4] Update Stock")
        print("[0] Back")

        choice = input("\nSelect Menu > ")

        if choice == "1":
            process_new_sale()

        elif choice == "2":
            cancel_sale()

        elif choice == "3":
            check_stock()

        elif choice == "4":
            update_stock()

        elif choice == "0":
            break

        else:
            print("Invalid Menu")


# Process New Sale
def process_new_sale():

    conn = get_connection()
    cursor = conn.cursor()

    print("\n")
    print("=====================================")
    print("       PROCESS NEW SALE")
    print("=====================================")

    store_id = int(
        input("Store ID > ")
    )

    items = {}
    total_price = 0

    while True:

        barcode = input(
            "\nBarcode (DONE=Finish) > "
        )

        if barcode.upper() == "DONE":
            break

        quantity = int(
            input("Quantity > ")
        )

        # 상품 조회
        cursor.execute("""
        SELECT
            barcode,
            name,
            price
        FROM Product
        WHERE barcode = ?
        """, (barcode,))

        product = cursor.fetchone()

        if not product:

            print("Invalid Barcode")
            continue

        # 재고 조회
        cursor.execute("""
        SELECT quantity
        FROM Stocks
        WHERE storeId = ?
        AND productBarcode = ?
        """, (
            store_id,
            barcode
        ))

        stock = cursor.fetchone()

        if not stock:

            print("Stock record not found.")
            continue

        # 이미 담긴 수량 계산
        existing_qty = 0

        if barcode in items:
            existing_qty = items[barcode]["quantity"]

        requested_qty = existing_qty + quantity

        if requested_qty > stock["quantity"]:

            print(
                f"Insufficient Stock "
                f"(Current: {stock['quantity']})"
            )
            continue

        subtotal = product["price"] * quantity

        total_price += subtotal

        if barcode in items:

            items[barcode]["quantity"] += quantity

        else:

            items[barcode] = {
                "quantity": quantity,
                "price": product["price"],
                "name": product["name"]
            }

        print(
            f"{product['name']} 추가됨 "
            f"({subtotal:,}원)"
        )

    if not items:

        print("No Items")
        conn.close()
        return

    print(
        f"\nTotal Price : "
        f"{total_price:,}원"
    )

    confirm = input(
        "Register Sale? (Y/N) > "
    )

    if confirm.upper() != "Y":

        conn.close()
        return

    # -------------------------
    # 판매 직전 재고 재검증
    # -------------------------

    for barcode, item in items.items():

        cursor.execute("""
        SELECT quantity
        FROM Stocks
        WHERE storeId = ?
        AND productBarcode = ?
        """, (
            store_id,
            barcode
        ))

        stock = cursor.fetchone()

        if stock["quantity"] < item["quantity"]:

            print(
                f"\nStock changed."
                f"\nSale cancelled."
            )

            conn.close()
            return

    # -------------------------
    # Sales 생성
    # -------------------------

    cursor.execute("""
    INSERT INTO Sales(
        saleDate,
        totalPrice,
        customerId,
        storeId
    )
    VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        total_price,
        None,
        store_id
    ))

    sales_id = cursor.lastrowid

    # -------------------------
    # SalesItem 생성
    # -------------------------

    for barcode, item in items.items():

        cursor.execute("""
        INSERT INTO SalesItem(
            salesId,
            productBarcode,
            quantity,
            unitPrice
        )
        VALUES (?, ?, ?, ?)
        """, (
            sales_id,
            barcode,
            item["quantity"],
            item["price"]
        ))

        cursor.execute("""
        UPDATE Stocks
        SET quantity = quantity - ?
        WHERE storeId = ?
        AND productBarcode = ?
        """, (
            item["quantity"],
            store_id,
            barcode
        ))

    conn.commit()
    conn.close()

    print(
        "\n>> Sale Registered Successfully"
    )