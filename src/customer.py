from db_connection import get_connection


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
            print("Search Product")

        elif choice == "2":
            print("Browse Category")

        elif choice == "3":
            print("View Cart")

        elif choice == "4":
            print("Purchase")

        elif choice == "5":
            print("Order History")

        elif choice == "0":
            print("Logout")
            break

        else:
            print("Invalid Menu")

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