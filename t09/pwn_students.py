#!/usr/bin/env python3

import re
import requests

URL = "{{CHALLENGE_URL}}"

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as sess:
    # TODO implement exploit


    # Beispielcode zum Lesen und Modifizieren eines Session-Cookies mit requests:

    r = sess.get(f'https://scoreboard.sec.in.tum.de/scoreboard')
    COOKIE_NAME = "session"

    # Den Cookie mit dem Namen COOKIE_NAME lesen
    cookie = sess.cookies[COOKIE_NAME]
    print(cookie)

    # Den Cookie mit dem Namen COOKIE_NAME für die Domain "scoreboard.sec.in.tum.de"
    # auf den Wert "asdf" setzen
    sess.cookies.set(name = COOKIE_NAME, value="asdf", domain = "scoreboard.sec.in.tum.de")
