#!/usr/bin/env python3

from Crypto.Cipher import AES
from flask import Flask, redirect, render_template_string, request, session

import base64
import bcrypt
import collections
import json
import os
import subprocess
from flask.sessions import SessionInterface, SessionMixin

app = Flask(__name__)

# App metadata
if not os.path.exists('app-secret.key'):
    with open('app-secret.key', 'wb') as f:
        f.write(os.urandom(32))

with open('app-secret.key', 'rb') as f:
    SECRET_KEY = f.read()

NONCE_LENGTH = 12 # bytes (of the 16 byte IV, the rest is a automatically generated counter)

COOKIE_NAME = 'itsec-session'
COOKIE_LIFETIME = 3600 # seconds

User = collections.namedtuple('User', ('password_hash', 'command'))
USER_DB = {
    'admin':    User(b'$2b$12$RHOf472SiDS1rXo6mdUW6.B4Aww7f94kDaL9nNnzkIjTXqFntdJLa', '/bin/flag'),
    'testuser': User(b'$2b$12$o5BG0DdXVxkZoNickA4aBeiRsKnWq.i1.9S1GCC77jkLAWTcH0ycm', '/bin/date'),
}

# Session management
class Session(dict, SessionMixin):
    pass

class EncryptedSession(SessionInterface):
    def open_session(self, app, request):
        """ Read the contents of the session cookie and restore the contents of the session variable. 
        This function is automatically executed by Flask before the invokation of index().
        """
        # Get raw cookie
        raw_cookie = request.cookies.get(COOKIE_NAME)
        if not raw_cookie:
            return Session()
        # Decrypt and load cookie
        try:
            data = base64.b64decode(raw_cookie)
            ciphertext, nonce = data[:-NONCE_LENGTH], data[-NONCE_LENGTH:]
            plaintext = AES.new(SECRET_KEY, AES.MODE_CTR, nonce=nonce).decrypt(ciphertext)
            return Session(json.loads(plaintext.decode()))
        except:
            return Session()
            
    def save_session(self, app, session, response):
        """ Serialize the session variable back to json and store it in a session cookie client-side. 
        This function is automatically executed by Flask after the invokation of index().
        """
        nonce = os.urandom(NONCE_LENGTH)
        plaintext = json.dumps(session).encode()
        print(plaintext)
        ciphertext = AES.new(SECRET_KEY, AES.MODE_CTR, nonce=nonce).encrypt(plaintext)
        raw_cookie = base64.b64encode(ciphertext + nonce)
        response.set_cookie(COOKIE_NAME, raw_cookie.decode(), max_age=COOKIE_LIFETIME)

app = Flask(__name__)
app.session_interface = EncryptedSession()

# Template
TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>TUMtime</title>
  </head>
  <body>
    <h1>TUMtime <small><small>by I20</small></small></h1>
  {% if site == "main" %}
    <p>Welcome back, {{ user }}</p>
    <p>It is now <b>{{ output }}</b></p>
  {% elif site == "login" %}
    <form method="POST" action="/login">
        <label for="username">Username: </label><input type="text" name="username" placeholder="Username"><br>
        <label for="password">Password: </label><input type="password" name="password" placeholder="Password"><br>
        <input type="submit" value="Log in">
    </form>
    <span style="color: red;">{{ warning }}</span>
    <p><small>To test TUMtime, log in with username <code>testuser</code> and password <code>foobar</code></small></p>
  {% endif %}
  </body>
</html>"""

@app.route('/')
def index():
    if "user" not in session:
        return redirect(f'/login')
    user = session['user']
    return render_template_string(TEMPLATE, site = "main", user = user, output = subprocess.check_output([USER_DB[user].command]).decode().strip())

@app.route("/logout")
def logout():
    del session['user']
    return redirect(f'/{code}/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form.get('username'), request.form.get('password')
        if not username or not password or not username in USER_DB or not bcrypt.checkpw(password.encode(), USER_DB[username].password_hash):
            return render_template_string(LOGIN_SCREEN, warning = 'Invalid username or password')
        session['user'] = username
        return redirect(f'/')
    return render_template_string(TEMPLATE, site = "login", warning = '')
