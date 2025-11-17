#!/usr/bin/env python3
import requests

# Name of the cookie
COOKIE = "session"

with requests.Session() as session:
    # Example how to modify a session cookie using requests.
    # You need to modifiy the following code so it fits the homework task
    r = session.get(f'https://scoreboard.sec.in.tum.de/scoreboard')
    cookie = session.cookies[COOKIE]
    print(session.cookies)
    session.cookies.set(name = COOKIE, value="asdf", domain = "scoreboard.sec.in.tum.de")
    
    # Cookie is now modified for this (and the following) requests
    r = session.get(f'https://scoreboard.sec.in.tum.de')
