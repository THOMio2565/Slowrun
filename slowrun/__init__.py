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


def format_seconds(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    parts = []
    if h > 0:
        parts.append(f"{h} h")
    if m > 0 or h > 0:
        parts.append(f"{m}min")
    parts.append(f"{s}s")
    return " ".join(parts)


app = fl.Flask(__name__)
app.jinja_env.filters["format_seconds"] = format_seconds


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
    return fl.render_template("index.html", games=games, runs=runs, articles=articles)
    resp = make_response(fl.render_template("index.html"))
    resp.set_cookie("username", request.form.get("username"))
    return resp


@app.route("/rankings/<id>")
def rankings_render(id):
    cursor = get_connection().cursor()
    game = cursor.execute(
        """
        SELECT name
                          
        FROM game
                          
        WHERE id = ?
    """,
        [id],
    ).fetchone()
    runs = cursor.execute(
        """
            SELECT slowrun.id, slowrun.time, slowrun.date, user.name AS user

            FROM slowrun

            JOIN register ON slowrun.register_id = register.id
            JOIN user ON register.user_id = user.id
            JOIN game ON register.game_id = game.id 

            WHERE game.id = ?

            ORDER BY slowrun.time DESC
    """,
        [id],
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
        """,
        [id],
    ).fetchall()
    categories = cursor.execute(
        """
            SELECT categories.name, game.id 
            
            FROM categories

            JOIN game ON categories.game_id = game.id
            
            WHERE game.id = ? 
        """,
        [id],
    )
    return fl.render_template(
        "Rank_Tetris.html",
        game=game,
        runs=runs,
        articles=articles,
        categories=categories,
    )


@app.route("/login", methods=["GET", "POST"])
def login_render():
    error = None
    cursor = get_connection().cursor()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Vérifier si l'utilisateur existe
        cursor.execute("SELECT * FROM user WHERE name = ?", (username,))
        user = cursor.fetchone()

        if user:
            # Vérifier le mot de passe
            if user["password"] == password:
                fl.session["user_id"] = user["id"]
                fl.session["username"] = user["name"]
                return fl.redirect(fl.url_for("user_render", id=user["id"]))
            else:
                error = "Mot de passe incorrect !"
        else:
            # Si l'utilisateur n'existe pas, on l'ajoute
            cursor.execute(
                "INSERT INTO user (name, date, password) VALUES (?, DATE('now'), ?)",
                (username, password),
            )
            cursor.commit()
            cursor.close()

            # Récupérer l'utilisateur après l'insertion
            user = cursor.execute(
                "SELECT * FROM user WHERE name = ?", (username,)
            ).fetchone()

            # Création de la session
            fl.session["user_id"] = user["id"]
            fl.session["username"] = user["name"]
            return fl.redirect(fl.url_for("user_render", id=user["id"]))

    return fl.render_template("Login.html", error=error)


@app.route("/inscription", methods=["GET", "POST"])
def inscription_render():
    error = None
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        existing_user = cursor.execute(
            "SELECT name FROM user WHERE name = ? OR email = ?", (name, email)
        ).fetchone()

        if existing_user:
            error = "Le nom d'utilisateur ou mail est déjà utilisé !"
        else:
            cursor.execute(
                "INSERT INTO user (name, email, date, password) VALUES (?, ?, DATE('now'), ?)",
                (name, email, password),
            )
            conn.commit()

            user_id = cursor.lastrowid
            cursor.close()

            return fl.redirect(fl.url_for("user_render", id=user_id))

    return fl.render_template("inscription.html", error=error)


@app.route("/run", methods=["GET", "POST"])
def run_render():
    cursor = get_connection().cursor()
    if request.method == "POST":
        commentaire = request.form["commentaire"]
        user_id = 1  # À adapter selon ton système d'authentification ou mettre session["user_id"] pour mettre en dur

        # Insérer le commentaire dans la base de données
        cursor.execute(
            "INSERT INTO commentaires (commentaire, user_id) VALUES (?, ?)",
            (commentaire, user_id),
        )
        cursor.commit()
        cursor.close()

        return fl.redirect("/")  # Recharge la page après soumission

    # Récupérer les commentaires de la base
    commentaires = cursor.execute(
        "SELECT * FROM commentaires ORDER BY id DESC"
    ).fetchall()
    cursor.close()
    return fl.render_template("Detailed_Run.html", commentaires=commentaires)


@app.route("/poster_run", methods=["POST"])
def poster_run():
    cursor = get_connection().cursor()

    game_name = request.form["game"]
    time = request.form["time"]
    date = request.form["date"]

    game_id = cursor.execute(
        """SELECT id FROM game WHERE name = ?""", (game_name)
    ).fetchone()
    register_id = cursor.execute(
        """
        SELECT id FROM register
        WHERE game_id = ?
        """, (game_id)
    ).fetchone()

    if game_id and register_id:
        cursor.execute(
            """INSERT INTO slowrun (register_id, time) VALUES (?, ?)""",
            (register_id["id"], time),
        )
        cursor.commit()
        cursor.close()

        return fl.redirect(fl.url_for("index_render"))

@app.route("/search")
def search_render():
    query = request.args.get('query', '').strip()
    games = []

    if query:
        cursor = get_connection().cursor()

        games = cursor.execute(
            """
            SELECT id, name FROM game
            WHERE name LIKE ?
            ORDER BY name
            """,
            (f'%{query}%',)
        ).fetchall()

        cursor.close()
    else:
        cursor = get_connection().cursor()
        games = cursor.execute(
            """
            SELECT id, name FROM game
            ORDER BY name
            """
        ).fetchall()
        cursor.close()

    return fl.render_template("games_list.html", games=games, query=query)


@app.route("/user/<id>")
def user_render(id):
    return fl.render_template("user.html")


@app.route("/Actus")
def actus_render():
    return fl.render_template("Actus.html")


@app.route("/cookies")
def index():
    username = request.cookies.get("user")

@app.errorhandler(404)
def page_not_found(e):
    return fl.render_template("404.html"), 404

