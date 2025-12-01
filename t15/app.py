from flask import Flask, render_template_string, session, request, flash
import secrets
import os
import re
import pickle
import time
import random
import subprocess

from flask.sessions import SessionInterface, SessionMixin

TOKEN = re.compile(r"[0-9a-f]{16}")
SESSION_PATH = "session_store/"
try:
    os.makedirs(SESSION_PATH)
except FileExistsError:
    pass
os.chmod(SESSION_PATH, 0o700)

class Session(dict, SessionMixin):
    def __init__(self, sid):
        self.sid = sid

# Assume that the Session Interface is secure.
# You can not modify it since it is stored on the servers disk.
class FileSessions(SessionInterface):
    def new_session(self):
        sid = secrets.token_hex(16)
        return Session(sid)

    def cleanup_session(self):
        threshold = time.time() - 20*60
        for x in os.scandir(SESSION_PATH):
            s = x.stat()
            if s.st_mtime < threshold:
                os.unlink(x)

    def open_session(self, app, request):
        sid = request.cookies.get("sid")
        if not sid or not TOKEN.match(sid):
            # There is no active session or an invalid one -> create an empty one
            return self.new_session()

        # There is an active session. Restore state from disk
        try:
            with open(SESSION_PATH + "/" + sid, "rb") as f:
                session = pickle.load(f)
            return session
        except FileNotFoundError:
            return self.new_session()
                
    def save_session(self, app, session, response):
        # Save some cpu cycles by garbage collecting old sessions only in about 10 percent
        # of the requests
        if random.random() < 0.1:
            self.cleanup_session()
        if session.modified:
            with open(SESSION_PATH + "/" + session.sid, "wb") as f:
                pickle.dump(session, f)

        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        response.set_cookie("sid", session.sid, httponly=True, domain=domain, path=path, samesite="Strict")

app = Flask(__name__)
app.session_interface = FileSessions()

page = """
<!doctype html>
<html>
<head>
    <title>TUMLottery!</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='pico.slim.min.css') }}">
</head>
<body>
<main class="container">
<header>
<h1><img src="/static/tum.svg" style="height:0.8em; position:relative; top:-3px"> Lottery</h1>
</header>
<main style="max-width: 800px; margin: 20px auto; border: 1px solid #aaa; padding: 1em">

This days lottery nubmers are is:

<div style="font-size: 1.5em; text-align: center; margin: 0.75em 0em">{{rand}}</div>

{% if guess %}
Your guess was
<div style="font-size: 1.5em; text-align: center; margin: 0.75em 0em">{{guess}}</div>
{% if flag %}
This is correct! Congratz! You won the lottery and your price is this flag:
<div>{{flag}}</div>
{% else %}
This is <b>not</b> correct! Stay strong! You might have more luck next time! <a href="/">Try again</a>
{% endif %}
{% else %}
Can you predict the lottery numbers of tommorow?

<form action="/" method="post" style="text-align: center; margin: 0.8em 0em; display: block">
<input type="text" name="guess" placeholder="Your guess">
<input type="submit" value="Guess">
</form>
{% endif %}
</main>
</body>
</html>
"""

u32 = lambda x: x & ((1 << 32)-1)

def randgen_xorshift32():
    if not "state" in session:
        session['state'] = secrets.randbits(32)
    x = session["state"]
    x ^= u32(x << 13);
    x ^= u32(x >> 17);
    x ^= u32(x << 5);
    session["state"] = x
    return x

@app.route("/", methods=["POST", "GET"])
def index():
    print(session)
    number = 1000000 + randgen_xorshift32() % 2**24 # Lottery numbers should have enough digits and should not be too large!
    number = f"{number:08}"
    flag = None
    if guess := request.form.get("guess"):
        session["guess"] = guess

        if number == guess:
            flag = subprocess.check_output("/bin/flag")
    return render_template_string(page, rand=number, guess=guess, flag=flag)
