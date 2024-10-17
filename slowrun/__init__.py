import flask as fl

app = fl.Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/index")
def accueil_render():
    return fl.render_template('index.html')

@app.route("/rankings")
def rankings_render():
    return fl.render_template('rank_tetris.html')

