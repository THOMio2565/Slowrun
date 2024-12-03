import sqlite3
from pathlib import Path

db = sqlite3.connect('slowrun.db')
sql = Path('slowrun/database/model.sql').read_text()
test = Path('slowrun/database/test.sql').read_text()
db.cursor().executescript(sql)
db.cursor().executescript(test)
db.commit()