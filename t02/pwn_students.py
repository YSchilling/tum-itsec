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
    flag = extract_flag_from_string("https://t02-a4b4d85430ba5c10.itsec.sec.in.tum.de/admin")
    print(flag)