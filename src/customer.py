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
            print("Login")

        elif choice == "4":
            break

        else:
            print("Invalid Menu")