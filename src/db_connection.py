import sqlite3

DB_PATH = "database/emart.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)

    # 컬럼명으로 접근 가능하게 설정
    conn.row_factory = sqlite3.Row

    # 외래키 활성화
    conn.execute("PRAGMA foreign_keys = ON")

    return conn