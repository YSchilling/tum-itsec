#!/usr/bin/env python3

import requests
import re

#TODO Change to your personal URL from the Scoreboard
URL = "{{CHALLENGE_URL}}"

NUMBER_REGEX = re.compile(r"\d{7,16}")

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as s:
    resp = s.get(URL)
    number = NUMBER_REGEX.search(resp.text).group(0)

    print(f"[+] Got number {number} from server")

    # TODO: Guess the right lottory draw *somehow*
    guessed_number = "0000000"
    resp = s.post(URL, data={"guess": guessed_number})
    if m := extract_flag_from_string(resp.text):
        print(f"[+] Flag: {m.group(0)}")
    else:
        print("[+] No flag :'(")
        print(resp.text)
