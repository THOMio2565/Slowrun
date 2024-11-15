import flask as fl
import sqlite3
from pathlib import Path

db = Path(__file__).parents[1] / 'slowrun.db'


def get_connection():
    """Get connection to database."""
    connection = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys')
    cursor.close()
    return connection

app = fl.Flask(__name__)


@app.route("/")
def index_render():
    cursor = get_connection().cursor()
    games = cursor.execute('''
            SELECT *
            FROM game
        ''').fetchall()
    runs = cursor.execute('''
            SELECT slowrun.time, game.name AS game, game.categories, user.name AS user

            FROM slowrun

            JOIN register ON slowrun.register_id = register.id
            JOIN game ON register.game_id = game.id
            JOIN user ON register.user_id = user.id

            ORDER BY slowrun.time DESC

            LIMIT 2
        ''').fetchall()
    return fl.render_template('index.html', games=games, runs=runs)

@app.route("/rankings")
def rankings_render():
    return fl.render_template('rank_tetris.html')