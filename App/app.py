from flask import Flask, render_template

# User defined imports
from database import setup_database

# Globals
app = Flask(__name__)

@app.before_first_request
def run_on_startup():
    global DB_CONNECTION
    DB_CONNECTION = setup_database()

# Home Page Route
@app.route("/")
def home():
    return render_template("index.html")

# Search API for running main part of the Engine
@app.route("/search")
def search():
    # run search on the database.
    dbCursor=DB_CONNECTION.cursor()

    return {} # TODO return rendered HTML results so the front end can display them appropriately without more Javascript
app.run()
