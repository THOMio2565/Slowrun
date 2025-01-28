import flask as fl
import sqlite3
from pathlib import Path
from flask import request

db = Path(__file__).parents[1] / "test.db"


def get_connection():
    """Get connection to database."""
    connection = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys")
    cursor.close()
    return connection


app = fl.Flask(__name__)


@app.route("/")
def index_render():
    cursor = get_connection().cursor()
    games = cursor.execute(
        """
            SELECT *

            FROM game

            ORDER BY count DESC
            
            LIMIT 4
        """
    ).fetchall()
    runs = cursor.execute(
        """
            SELECT slowrun.time, game.name AS game, user.name AS user

            FROM slowrun

            JOIN register ON slowrun.register_id = register.id
            JOIN game ON register.game_id = game.id
            JOIN user ON register.user_id = user.id

            ORDER BY slowrun.time DESC

            LIMIT 2
        """
    ).fetchall()
    articles = cursor.execute(
        """
            SELECT news.title, game.name AS game, user.name AS user

            FROM news

            JOIN game ON news.game_id = game.id
            JOIN user ON news.user_id = user.id

            ORDER BY news.id DESC

            LIMIT 4
        """
    ).fetchall()
    return fl.render_template("index.html", games=games, runs=runs, articles = articles)
    resp = make_response(fl.render_template("index.html"))
    resp.set_cookie('username', request.form.get("username"))
    return resp


@app.route("/rankings/<id>")
def rankings_render(id):
    cursor = get_connection().cursor()
    game = cursor.execute(
        """
        SELECT name
                          
        FROM game
                          
        WHERE id = ?
    """, [id]
    ).fetchone()
    runs = cursor.execute(
        """
            SELECT slowrun.time, slowrun.date, user.name AS user

            FROM slowrun

            JOIN register ON slowrun.register_id = register.id
            JOIN user ON register.user_id = user.id
            JOIN game ON register.game_id = game.id 

            WHERE game.id = ?

            ORDER BY slowrun.time DESC
    """, [id]
    ).fetchall()
    articles = cursor.execute(
        """
            SELECT news.title, game.name AS game, user.name AS user

            FROM news

            JOIN game ON news.game_id = game.id
            JOIN user ON news.user_id = user.id

            WHERE game.id = ?

            ORDER BY news.id DESC

            LIMIT 4
        """, [id]
    ).fetchall()
    categories = cursor.execute(
        """
            SELECT categories.name, game.id 
            
            FROM categories

            JOIN game ON categories.game_id = game.id
            
            WHERE game.id = ? 
        """, [id]
    )
    return fl.render_template("Rank_Tetris.html", game=game, runs=runs, articles=articles, categories=categories)

@app.route("/login", methods=['GET', 'POST'])
def login_render():
    error = None
    cursor = get_connection().cursor()
    if request.method == 'POST':
        user = cursor.execute("""
        SELECT * FROM user
        WHERE name = ? AND  password = ?
        """, [request.form['username'], request.form['password']]).fetchone()
        if user:
            print(user)
        else:
            error = 'Invalid username/password'
    return fl.render_template('login.html', error=error)