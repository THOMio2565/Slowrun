import flask as fl
import sqlite3
from pathlib import Path
from flask import request, session, flash, redirect, url_for
from functools import wraps
import hashlib

db = Path(__file__).parents[1] / "slowrun.db"


def get_connection():
    """Get connection to database."""
    connection = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()
    return connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page', 'error')
            return redirect(url_for('login_render'))
        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    if 'user_id' not in session:
        return None

    with get_connection() as conn:
        cursor = conn.cursor()
        user = cursor.execute(
            "SELECT id, name, email FROM user WHERE id = ?",
            (session['user_id'],)
        ).fetchone()
        return user

def format_seconds(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    parts = []
    if h > 0:
        parts.append(f"{h}h")
    if m > 0 or h > 0:
        parts.append(f"{m}min")
    parts.append(f"{s}s")
    return " ".join(parts)


app = fl.Flask(__name__)
app.secret_key = 'votre_cle_secrete_tres_longue_et_complexe_123456789'
app.jinja_env.filters["format_seconds"] = format_seconds


@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())


@app.route("/")
def index_render():
    cursor = get_connection().cursor()
    games = cursor.execute(
        """
        SELECT *
        FROM game
        ORDER BY count DESC LIMIT 4
        """
    ).fetchall()
    runs = cursor.execute(
        """

            SELECT slowrun.time, slowrun.date, game.name AS game, user.name AS user, slowrun.id AS link

            FROM slowrun

            JOIN game ON slowrun.game_id = game.id
            JOIN user ON slowrun.user_id = user.id
        ORDER BY slowrun.date DESC
            LIMIT 2
        """
    ).fetchall()
    articles = cursor.execute(
        """
        SELECT news.title, game.name AS game, user.name AS user
        FROM news
            JOIN game
        ON news.game_id = game.id
            JOIN user ON news.user_id = user.id
        ORDER BY news.id DESC
            LIMIT 4
        """
    ).fetchall()
    cursor.close()

    resp = fl.make_response(fl.render_template("index.html", games=games, runs=runs, articles=articles))
    if request.form.get("username") :
        resp.set_cookie("username", request.form.get("username"))
    return resp


@app.route("/rankings/<id>")
def rankings_render(id):
    cursor = get_connection().cursor()
    game = cursor.execute(
        """
        SELECT name, id
        FROM game
        WHERE id = ?
        """,
        [id],
    ).fetchone()
    runs = cursor.execute(
        """
        SELECT slowrun.id, slowrun.time, slowrun.date, user.name AS user, user.id as profile
        FROM slowrun
            JOIN user
        ON slowrun.user_id = user.id
            JOIN game ON slowrun.game_id = game.id
        WHERE game.id = ?
        ORDER BY slowrun.time DESC
        """,
        [id],
    ).fetchall()
    articles = cursor.execute(
        """
        SELECT news.title, game.name AS game, user.name AS user
        FROM news
            JOIN game
        ON news.game_id = game.id
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
    ).fetchall()
    cursor.close()
    return fl.render_template(
        "rankings.html",
        game=game,
        runs=runs,
        articles=articles,
        categories=categories,
        id=id
    )


@app.route("/login", methods=["GET", "POST"])
def login_render():
    if 'user_id' in session:
        return redirect(url_for('index_render'))

    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Please fill all fields."
        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM user WHERE name = ?", (username,))
            user = cursor.fetchone()

            if user and user["password"] == hash_password(password):
                session['user_id'] = user["id"]
                session['username'] = user["name"]
                cursor.close()

                flash(f"Bienvenue {user['name']} !", "success")

                return redirect(url_for('index_render'))
            else:
                error = "Username or password is incorrect."

            cursor.close()

    return fl.render_template("login.html", error=error)



@app.route("/signup", methods=["GET", "POST"])
def signup_render():
    if 'user_id' in session:
        return redirect(url_for('index_render'))

    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validation des données
        if not all([name, email, password]):
            error = "Please fill all fields."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        else:
            conn = get_connection()
            cursor = conn.cursor()

            existing_user = cursor.execute(
                "SELECT name FROM user WHERE name = ? OR email = ?", (name, email)
            ).fetchone()

            if existing_user:
                error = "Username or email is already in use."
            else:
                hashed_password = hash_password(password)
                print(hashed_password)

                cursor.execute(
                    "INSERT INTO user (name, email, date, password) VALUES (?, ?, DATE('now'), ?)",
                    (name, email, hashed_password)
                )
                conn.commit()

                user_id = cursor.lastrowid

                session['user_id'] = user_id
                session['username'] = name

                cursor.close()

                return redirect(url_for('index_render'))

            cursor.close()

    return fl.render_template("signup.html", error=error)

@app.route("/logout")
def logout():
    username = session.get('username', 'Utilisateur')
    session.clear()
    return redirect(url_for('index_render'))


@app.route("/run/<int:id>", methods=["GET", "POST"])
def run_render(id):
    cursor = get_connection().cursor()

    details = cursor.execute(
        """
        SELECT slowrun.id,
               slowrun.time,
               game.name AS game,
               game.id   AS game_link,
               user.name AS user, 
               user.id AS profile, 
               categories.name AS category
        FROM slowrun
            JOIN game ON slowrun.game_id = game.id
            JOIN user ON slowrun.user_id = user.id
            JOIN categories ON slowrun.category_id = categories.id
        WHERE slowrun.id = ?
        """, (id,)
    ).fetchone()

    if not details:
        return redirect(url_for('index_render'))

    comments = cursor.execute(
        """
        SELECT c.comment, u.name as user_name, c.id as comment_id
        FROM comments c
                 JOIN user u ON c.user_id = u.id
        WHERE c.run_id = ?
        ORDER BY c.id DESC
        """, (id,)).fetchall()

    cursor.close()

    return fl.render_template("run.html", run=id, details=details, comments=comments)

@app.route("/comments/<int:run_id>", methods=["POST"])
def comments(run_id):
    if 'user_id' not in session:
        return redirect(url_for('login_render'))

    comment = request.form.get("comment", "").strip()
    user_id = session['user_id']

    if comment:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO comments (comment, user_id, run_id) VALUES (?, ?, ?)""",
            (comment, user_id, run_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
    else:
        flash("Comment cannot be empty", "error") # convert to error variable

    return redirect(url_for('run_render', id=run_id))

@app.route("/rankings/<int:id>", methods=["POST"])
@login_required
def poster_run(id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        game_name = id
        time_input = request.form.get("time", "").strip()
        date_input = request.form.get("date", "").strip()
        category_input = request.form.get("category", "").strip()

        user_id = session['user_id']

        if not all([game_name, time_input, date_input]):
            flash("All fields are required", "error") # convert to error variable
            return redirect(url_for("rankings_render", id=id))

        try:
            from datetime import datetime
            datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            return redirect(url_for("rankings_render", id=id))

        try:
            if ':' in time_input:
                time_parts = time_input.split(':')
                if len(time_parts) == 2:
                    minutes, seconds = map(int, time_parts)
                    time_seconds = minutes * 60 + seconds
                elif len(time_parts) == 3:
                    hours, minutes, seconds = map(int, time_parts)
                    time_seconds = hours * 3600 + minutes * 60 + seconds
                else:
                    raise ValueError("Invalid time format")
            else:
                time_seconds = int(float(time_input))
        except (ValueError, TypeError):
            return redirect(url_for("rankings_render", id=id))

        if time_seconds <= 0:
            return redirect(url_for("rankings_render", id=id))

        game_result = cursor.execute(
            "SELECT id, name FROM game WHERE id = ?",
            (game_name,)
        ).fetchone()

        if not game_result:
            available_games = cursor.execute(
                "SELECT name FROM game ORDER BY name LIMIT 10"
            ).fetchall()
            game_list = ", ".join([g["name"] for g in available_games])
            flash(f"Game '{game_name}' does not exist. List of games : {game_list}...", "error") #convert to error variable
            return redirect(url_for("rankings_render", id=id))

        game_id = game_result["id"]

        category_result = cursor.execute(
            "SELECT id, name FROM categories WHERE LOWER(name) = LOWER(?)",
            (category_input,)
        ).fetchone()

        if not category_result:
            available_categories = cursor.execute(
                """
                SELECT name FROM categories 
                    WHERE game_id = ?
                """, (game_id,)
            ).fetchall()
            categories_list = ", ".join([g["name"] for g in available_categories])
            flash(f"Category '{category_input}' does not exist for this game. Available categories : {categories_list}...", "error")
            return redirect(url_for("rankings_render", id=id))

        category_id = category_result["id"]

        cursor.execute(
            "INSERT INTO slowrun (time, date, user_id, game_id, category_id) VALUES (?, ?, ?, ?, ?)",
            (time_seconds, date_input, user_id, game_id, category_id)
        )

        conn.commit()

        username = session.get('username', 'Utilisateur')

    except sqlite3.Error as e:
        conn.rollback()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("rankings_render", id=id))


@app.route("/search")
def search_render():
    query = request.args.get('query', '').strip()
    cursor = get_connection().cursor()

    if query:
        games = cursor.execute(
            """
            SELECT id, name
            FROM game
            WHERE name LIKE ?
            ORDER BY name
            """,
            (f'%{query}%',)
        ).fetchall()
    else:
        games = cursor.execute(
            "SELECT id, name FROM game ORDER BY name"
        ).fetchall()

    cursor.close()
    return fl.render_template("games_list.html", games=games, query=query)


@app.route("/user/<int:id>")
def user_render(id):
    cursor = get_connection().cursor()

    user = cursor.execute(
        "SELECT id, name, email, date FROM user WHERE id = ?",
        (id,)
    ).fetchone()

    if not user:
        return redirect(url_for('index_render'))

    runs = cursor.execute(
        """
        SELECT slowrun.id as slowrun_id, slowrun.time, slowrun.date, game.name as game_name, game.id as link, categories.name as category_name
        FROM slowrun
                 JOIN game ON slowrun.game_id = game.id
                 LEFT JOIN categories ON slowrun.category_id = categories.id
        WHERE slowrun.user_id = ?
        ORDER BY slowrun.date DESC
        """,
        (id,)
    ).fetchall()

    run_count = cursor.execute(
        """SELECT COUNT(*) FROM slowrun WHERE user_id = ?""",
        (id,)
    ).fetchone()[0]

    cursor.close()
    return fl.render_template("user.html", user=user, runs=runs, run_count=run_count)


@app.route("/profile/<int:id>")
@login_required
def profile():
    return redirect(url_for('user_render', id=session['user_id']))


@app.route("/Actus")
def actus_render():
    return fl.render_template("news.html")


@app.errorhandler(404)
def page_not_found(e):
    return fl.render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)