import os
from pathlib import Path

_env_path = os.environ.get('EMART_DB_PATH')
if _env_path:
	DB_PATH = Path(_env_path).expanduser().resolve()
else:
	DB_PATH = Path(__file__).resolve().parent.parent / 'database' / 'emart.db'

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_PATH = str(DB_PATH)