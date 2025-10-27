from flask import Flask, request, session, redirect, render_template
import bcrypt
import os
import string
import subprocess

import socket

app = Flask(__name__)

if not os.path.exists("app-secret.key"):
    with open("app-secret.key", "wb") as f:
        f.write(os.urandom(32))

with open("app-secret.key", "rb") as f:
    app.secret_key = f.read()

allowed_users = {
    "admin": b'$2b$12$RHOf472SiDS1rXo6mdUW6.B4Aww7f94kDaL9nNnzkIjTXqFntdJLa',
    "testuser": b'$2b$12$o5BG0DdXVxkZoNickA4aBeiRsKnWq.i1.9S1GCC77jkLAWTcH0ycm'
}

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    d = {
        "amount": "0" if session["user"] != "admin" else subprocess.check_output("/bin/flag").decode()
    }

    return render_template("main.html", **d)

@app.route("/help")
def help():
    ln = request.args.get("ln", "English")

    if ln == "English":
        helptext = "This is a trusted banking website offered by TUM. No further help needed!"
    else:
        helptext = "We don't speak your language. Sorry!"

    return render_template("help.html", ln=ln, helptext=helptext)

@app.route("/logout")
def logout():
    if "user" in session:
        del session["user"]
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pw = request.form["password"]
        if username in allowed_users:
            if bcrypt.checkpw(pw.encode(), allowed_users[username]):
                session.permanent = True
                session["user"] = username
                return redirect("/")
            else: raise ValueError(f"Bad password: {pw!r}")
    return render_template("login.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        
        # Forward the link to the admin so that he can click on it
        # You do not need to get the technical details of the forwarding
        # process of the server to solve the task!
        text = request.form["contacttext"]
        address = (os.environ['ADMIN_CONTACT_HOST'], int(os.environ['ADMIN_CONTACT_PORT']))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        sock.sendall(request.host_url.encode() + b"\n")
        sock.sendall(text.encode())
        sock.close()
    return render_template("contact.html")
