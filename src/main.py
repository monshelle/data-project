import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from utils import header
from customer import consumer_menu, ensure_customer_tables
from dba import dba_menu
from olap import olap_menu
from reorder import reorder_menu
from supplier import supplier_menu


def main():
    ensure_customer_tables()
    while True:
        header('Emart DB Management System')
        print('  1. DBA Management')
        print('  2. OLAP')
        print('  3. Customer Interface')
        print('  4. Auto Reorder')
        print('  5. Supplier Interface')
        print('  0. Exit')
        c = input('\nSelect > ').strip()
        if c == '0':
            print('  Exiting...'); break
        elif c == '1': dba_menu()
        elif c == '2': olap_menu()
        elif c == '3': consumer_menu()
        elif c == '4': reorder_menu()
        elif c == '5': supplier_menu()


if __name__ == '__main__':
    main()
