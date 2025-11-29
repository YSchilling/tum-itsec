from flask import Flask, render_template_string, session, request, flash
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import subprocess
import json
import os

from flask.sessions import SessionInterface, SessionMixin

# App metadata
if not os.path.exists('app-secret.key'):
    with open('app-secret.key', 'wb') as f:
        f.write(os.urandom(32))

with open('app-secret.key', 'rb') as f:
    SECRET_KEY = f.read()

MAC_SIZE = 4

def mh5(x):
    state = 0

    # Apply padding
    x = x + b"\x80" # Terminate message with 0x80
    x = x + (MAC_SIZE - (len(x) % MAC_SIZE)) * b"\x00"

    # Split into chunks
    for i in range(0,len(x), MAC_SIZE):
        state += int.from_bytes(x[i:i+MAC_SIZE], byteorder="big")
        state &= (2**32 - 1)
    return state.to_bytes(length=MAC_SIZE, byteorder="big")

# Who needs integrity protection? I heared that encrypting all information
# with AES-CBC and store it in a session cookie client-side is fine!
class Session(dict, SessionMixin):
    pass

class EncryptedSession(SessionInterface):
    
    def open_session(self, app, request):
        """ Read the contents of the session cookie and restore the contents of the session variable. 
        This function is automatically executed by Flask before the invokation of index().
        """
        session = request.cookies.get("session")
        if not session:
            # There is no active session, lets create one
            return Session()

        # There is an active session. Check its integrity and use it.
        try:
            data = bytes.fromhex(session)
            mac, session_data = data[:MAC_SIZE], data[MAC_SIZE:]
            mac_p = mh5(SECRET_KEY + session_data)
            if not mac == mac_p:
                print(f"Integrity check failed {mac} {mac_p}")
                return Session()
            session_data = json.loads(session_data)
            return Session(session_data)
        except:
            # Some debugging info for your admins. You cannot see them client-side
            import traceback
            traceback.print_exc()
            # The active session has some problem: Create a new one, discard the old data...
            return Session()
                
    def save_session(self, app, session, response):
        """ Serialize the session variable back to json and store it in a session cookie client-side. 
        This function is automatically executed by Flask after the invokation of index().
        """
        session_json = json.dumps(session) # This will be: '{"u": "tester"}' for the page below
        session_json = session_json.encode()
        mac = mh5(SECRET_KEY + session_json)
        data = mac.hex() + session_json.hex()
        domain = self.get_cookie_domain(app)
        response.set_cookie("session", data, httponly=True, domain=domain, path="/", samesite="Strict")

app = Flask(__name__)
app.session_interface = EncryptedSession()

page = """
<!doctype html>
<html>
<head>
    <title>TUMTime v3!</title>
</head>
<body>
<div style="text-align: center">
<h1><span style="color: #0065bd">TUM</span>Time <span style="color: red; font-size: 0.7em; rotate: 30deg; display: inline-block">v3</span></h1>
</div>
<main style="max-width: 800px; margin: 20px auto; border: 1px solid #aaa; padding: 1em">

The time is:

<div style="font-size: 1.5em; text-align: center; margin: 0.75em 0em">{{time}}</div>
</main>
</body>
</html>
"""

@app.route("/")
def index():
    if "u" not in session:
        session["u"] = "tester"
    if session["u"] == "admin":
        time = subprocess.check_output("/bin/flag")
    else:
        time = subprocess.check_output("/bin/date")

    return render_template_string(page, time=time.decode())
