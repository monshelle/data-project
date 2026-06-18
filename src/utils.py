import sqlite3
import os
import sys
import unicodedata

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from db_config import DB_PATH

def conn():
    return sqlite3.connect(DB_PATH)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def sep(w=62): print('-' * w)
def dsep(w=62): print('=' * w)

def header(title):
    cls()
    dsep()
    print(f'  {title}')
    dsep()

def _dw(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ('W', 'F') else 1
               for c in str(s))

def wl(s, w: int) -> str:
    s = str(s)
    return s + ' ' * max(0, w - _dw(s))

def wr(s, w: int) -> str:
    s = str(s)
    return ' ' * max(0, w - _dw(s)) + s

def pause():
    input('\n[Enter] to continue...')
