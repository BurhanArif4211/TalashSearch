from flask import Flask, request, render_template
import json
# User defined imports
from database import *

# Globals
app = Flask(__name__)

# Home Page Route
@app.route("/")
def home():
    return render_template("index.html")

# Search API for running main part of the Engine
@app.route("/search",methods = ["POST"])
def search():
    if not request.method == 'POST' or not request.is_json:
        return "Database Error" # pranking the pentesters
    req = request.get_json()
    query = req.get("searchQuery")

    results = search_documents(DB_CONNECTION,query)
    if not results:
        return "<p>No Results found</p>"
    # TODO return rendered HTML results so the front end can display them appropriately without more Javascript
    html = ""
    for row in results:
        html += f"""
  <div class="text-white h-[100px] pb-[20px] bg-[#FFF3C8] rounded-xl">
    <div class="text-white pt-6 pr-6 text-gray-900">{row[1]}</div>
    <div class="text-blue-300 pr-6 text-[11px]"><a dir="ltr" target="_blank" href="{row[3]}">{row[3]}</a></div>
    <div class="text-[10px] pr-6 text-gray-500">{row[2]}</div>
  </div>\n"""
        

    return html

if __name__ == "__main__":
    global DB_CONNECTION
    DB_CONNECTION = setup_database()
    app.run()
