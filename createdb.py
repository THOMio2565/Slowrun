import sqlite3
from pathlib import Path

db = sqlite3.connect('slowrun.db')
sql = Path('slowrun/database/model.sql').read_text()
db.cursor().executescript(sql)
db.commit()