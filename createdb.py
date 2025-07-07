import sqlite3
from pathlib import Path

db_slowrun = Path('slowrun.db')
db_test = Path('test.db')
sql = Path('slowrun/database/model.sql').read_text()
#test = Path('slowrun/database/test.sql').read_text()

def create_db_file(db_connection, sql_script, db_path): # db_connection is found as "db" in the if statements; sql_script calls the right .sql file to execute when creating the database, db_path refers to the file name on creation
    with db_connection:
        db_connection.executescript(sql_script)
        print(f"Database '{db_path}' has been initialized.")

def delete_db_file(db_connection, db_path):
    db_connection.close()  # Closes the connection to the database so the file can be deleted
    if db_path.exists():
        db_path.unlink()  # unlink is used to delete the file
        print(f"Database file '{db_path}' has been deleted.")
    else:
        print(f"Database file '{db_path}' does not exist.")

# if db_slowrun.exists():
#     db = sqlite3.connect(db_slowrun)
#     delete_db_file(db, db_slowrun)
# db = sqlite3.connect(db_slowrun)
# create_db_file(db, sql, db_slowrun)
