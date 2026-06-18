from customer import customer_menu
from oltp import oltp_menu
from olap import olap_menu
from auto_reorder import auto_reorder_menu
from supplier import supplier_menu
from dba import dba_menu


def main():

    while True:

        print("\n")
        print("=====================================")
        print("         EMART SYSTEM")
        print("=====================================")
        print("[1] Customer")
        print("[2] Distributor-OLTP")
        print("[3] Distributor-OLAP")
        print("[4] Auto Reorder")
        print("[5] Supplier")
        print("[6] DBA")
        print("[0] Exit")

        choice = input("\nSelect Menu > ")

        if choice == "1":
            customer_menu()

        elif choice == "2":
            oltp_menu()

        elif choice == "3":
            olap_menu()

        elif choice == "4":
            auto_reorder_menu()

        elif choice == "5":
            supplier_menu()

        elif choice == "6":
            dba_menu()

        elif choice == "0":
            print("System Closed")
            break

        else:
            print("Invalid Menu")


if __name__ == "__main__":
    main()