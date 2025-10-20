#!/usr/bin/env python3

from flask import Flask, request
import subprocess
import sqlite3

app = Flask(__name__)

page_head = """
<!doctype html>
<html>
<head>
<title>TUMoogle!</title>
<style>
body {
    text-align: center;
}

h1 {
    font-family: sans-serif;
    color: #0065bd;
}
#results {
    margin-top: 10px;
    text-align: left;
}
</style>

</head>

<body>
    <h1>TUMoogle!</h1>
    <h2>The <i>excellent</i> search engine!</h2>
    <form action="/" method="get">
        <input type="text" name="q">
        <input type="submit" value="Search!">
    </form>
<div id="results">"""

page_footer = """
</div>
</body>
</html>
"""

def load_internet(db):
    db.execute("CREATE TABLE internet_index (id INT PRIMARY KEY, title TEXT, url TEXT, is_secret INT)")
    flag = subprocess.check_output("/bin/flag").decode()
    db.execute("""INSERT INTO internet_index VALUES
    (NULL, "Chair for IT Security", "http://www.sec.in.tum.de", 0),
    (NULL, "Technische Universität München (TUM)", "http://www.tum.de", 0),
    (NULL, "Heise", "http://www.heise.de", 0),
    (NULL, "Stack Overflow", "http://www.stackoverflow.com", 0),
    (NULL, "TUM Moodle", "http://moodle.tum.de", 0),
    (NULL, "TUM Online", "http://campus.tum.de", 0),
    (NULL, "Wikipedia", "http://www.wikipedia.de", 0),
    (NULL, "{}", "", 1)
    """.format(flag))

@app.route("/")
def index():
    q = request.args.get("q")
    print(q)
    page = ""
    if q:
        if len(q) >= 3:
            db = sqlite3.connect(":memory:", isolation_level=None)
            load_internet(db)
            cur = db.cursor()
            cur.execute("SELECT * FROM internet_index WHERE is_secret=0 AND title LIKE '%{}%'".format(q))
            page += "<h2>Results</h2>"
            for record in cur.fetchall():
                page = page + """<a href="{}">{}</a><br>""".format(record[2], record[1])
        else:
            page = "Search query to short!"
    return page_head + page + page_footer
