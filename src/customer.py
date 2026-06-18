from db_connection import get_connection
from datetime import datetime


#메뉴
def customer_menu():

    while True:

        print("\n")
        print("=====================================")
        print("           CUSTOMER")
        print("=====================================")
        print("[1] Initial Screen")
        print("[2] Sign Up")
        print("[3] Login")
        print("[4] Exit")

        choice = input("\nSelect Menu > ")

        if choice == "1":
            print("Initial Screen")

        elif choice == "2":
            sign_up()

        elif choice == "3":
            login()

        elif choice == "4":
            break

        else:
            print("Invalid Menu")


#회원 가입
def sign_up():

    print("\n[ SIGN UP ]\n")

    name = input("Name      : ")
    phone = input("Phone     : ")

    birthday = input("Birthday (Optional) : ")

    if birthday.strip() == "":
        birthday = None

    address = input("Address   : ")
    email = input("Email     : ")
    password = input("Password  : ")

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
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
        """,
        (
            name,
            phone,
            birthday,
            address,
            email,
            password,
            1      # Emart Distributor
        ))

        conn.commit()

        print("\n>> Sign Up Success!")

    except Exception as e:

        print("\n>> Sign Up Failed")
        print(e)

    finally:

        conn.close()

#로그인
def login():

    print("\n[ LOGIN ]\n")

    email = input("Email    : ")
    password = input("Password : ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM Customer
    WHERE email = ?
    AND password = ?
    """, (email, password))

    customer = cursor.fetchone()

    conn.close()

    if customer:

        print("\n>> Login Success!")

        customer_main(customer)

    else:

        print("\n>> Invalid Email or Password")

#customer login 후 main 화면
def customer_main(customer):

    while True:

        print("\n")
        print("=====================================")
        print(f" Welcome, {customer['name']}")
        print("=====================================")

        print("[1] Search Product")
        print("[2] Browse Category")
        print("[3] View Cart")
        print("[4] Purchase")
        print("[5] Order History")
        print("[0] Logout")

        choice = input("\nSelect Menu > ")

        if choice == "1":
            search_product(customer)

        elif choice == "2":
            browse_category()

        elif choice == "3":
            view_cart(customer)

        elif choice == "4":
            print("Purchase")

        elif choice == "5":
            print("Order History")

        elif choice == "0":
            print("Logout")
            break

        else:
            print("Invalid Menu")


# 상품명 검색 시 결과 보여주는 기능
def search_product(customer):

    keyword = input("\nEnter Product Name > ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        P.barcode,
        P.name,
        P.specification,
        P.price,
        B.name AS brand_name
    FROM Product P
    LEFT JOIN Brand B
        ON P.brandId = B.id
    WHERE P.name LIKE ?
    """, (f"%{keyword}%",))

    products = cursor.fetchall()

    if not products:

        print("\nNo products found.")
        conn.close()
        return

    print("\n=====================================")
    print("         SEARCH RESULT")
    print("=====================================")

    for product in products:

        print(
            f"Barcode : {product['barcode']}\n"
            f"Name    : {product['name']}\n"
            f"Spec    : {product['specification']}\n"
            f"Price   : {product['price']}원\n"
            f"Brand   : {product['brand_name']}\n"
        )

        print("-------------------------------------")

    barcode = input(
        "\nEnter Barcode To Add Cart (0=Back) > "
    )

    if barcode == "0":

        conn.close()
        return

    quantity = int(
        input("Quantity > ")
    )

    conn.close()

    add_to_cart(
        customer["id"],
        barcode,
        quantity
    )


#Browse Category
def browse_category():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT name
    FROM ProductType
    ORDER BY name
    """)

    categories = cursor.fetchall()

    if not categories:
        print("\n등록된 카테고리가 없습니다.")
        conn.close()
        return

    print("\n=====================================")
    print("            CATEGORY")
    print("=====================================")

    for idx, category in enumerate(categories, start=1):
        print(f"[{idx}] {category['name']}")

    print("[0] Back")

    choice = input("\nSelect Category > ")

    if choice == "0":
        conn.close()
        return

    try:
        category_name = categories[int(choice)-1]["name"]
    except:
        print("Invalid Category")
        conn.close()
        return

    cursor.execute("""
    SELECT
        P.name,
        P.price,
        B.name
    FROM Product P
    JOIN ProductType PT
        ON P.barcode = PT.productBarcode
    LEFT JOIN Brand B
        ON P.brandId = B.id
    WHERE PT.name = ?
    """, (category_name,))

    products = cursor.fetchall()

    print(f"\n[{category_name} 상품 목록]\n")

    for product in products:
        print(
            f"{product['name']} | "
            f"{product['price']}원 | "
            f"{product[2]}"
        )

    conn.close()


#장바구니 추가
def add_to_cart(customer_id, barcode, quantity):

    conn = get_connection()
    cursor = conn.cursor()

    # 장바구니 존재 여부 확인

    cursor.execute("""
    SELECT id
    FROM Cart
    WHERE customerId = ?
    """, (customer_id,))

    cart = cursor.fetchone()

    if cart:

        cart_id = cart["id"]

    else:

        cursor.execute("""
        INSERT INTO Cart(
            customerId,
            createdAt
        )
        VALUES (?, ?)
        """, (
            customer_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        cart_id = cursor.lastrowid

    # 이미 담겨있는 상품인지 확인

    cursor.execute("""
    SELECT quantity
    FROM CartItem
    WHERE cartId = ?
    AND productBarcode = ?
    """, (cart_id, barcode))

    item = cursor.fetchone()

    if item:

        cursor.execute("""
        UPDATE CartItem
        SET quantity = quantity + ?
        WHERE cartId = ?
        AND productBarcode = ?
        """, (
            quantity,
            cart_id,
            barcode
        ))

    else:

        cursor.execute("""
        INSERT INTO CartItem(
            cartId,
            productBarcode,
            quantity
        )
        VALUES (?, ?, ?)
        """, (
            cart_id,
            barcode,
            quantity
        ))

    conn.commit()
    conn.close()

    print("\n>> Added To Cart")

#장바구니 확인
def view_cart(customer):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id
    FROM Cart
    WHERE customerId = ?
    """, (customer["id"],))

    cart = cursor.fetchone()

    if not cart:

        print("\nCart is empty.")
        conn.close()
        return

    cart_id = cart["id"]

    cursor.execute("""
    SELECT
        P.name,
        CI.quantity,
        P.price,
        CI.quantity * P.price
    FROM CartItem CI
    JOIN Product P
        ON CI.productBarcode = P.barcode
    WHERE CI.cartId = ?
    """, (cart_id,))

    items = cursor.fetchall()

    print("\n=====================================")
    print("            MY CART")
    print("=====================================")

    total = 0

    for item in items:

        print(
            f"{item[0]:20}"
            f"{item[1]}개  "
            f"{item[3]:,}원"
        )

        total += item[3]

    print("-------------------------------------")
    print(f"TOTAL : {total:,}원")

    conn.close()
