import os

DB_PATH = os.environ.get('EMART_DB_PATH', 'database/emart.db')
os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)