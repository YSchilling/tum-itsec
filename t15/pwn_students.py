#!/usr/bin/env python3

import requests
import re


#TODO Change to your personal URL from the Scoreboard
URL = "https://t15-bfd6cf936fd8b844.itsec.sec.in.tum.de"

NUMBER_REGEX = re.compile(r"\b\d{8}\b")

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

def u32(x):
    return x & 0xFFFFFFFF

def randgen_xorshift32(x):
    x ^= u32(x << 13)
    x = u32(x)
    x ^= u32(x >> 17)
    x = u32(x)
    x ^= u32(x << 5)
    return u32(x)

def reverse_xorshift32(y):
    x2 = y
    shift = 5
    x2 ^= u32(x2 << shift)
    x2 = u32(x2)
    x2 ^= u32(x2 << (shift * 2))
    x2 = u32(x2)
    x2 ^= u32(x2 << (shift * 4))
    x2 = u32(x2)

    x1 = x2
    shift = 17
    x1 ^= u32(x1 >> shift)
    x1 = u32(x1)

    x0 = x1
    shift = 13
    x0 ^= u32(x0 << shift)
    x0 = u32(x0)
    x0 ^= u32(x0 << (shift * 2))
    x0 = u32(x0)

    return x0

with requests.Session() as s:
    resp = s.get(URL)
    num1 = int(NUMBER_REGEX.search(resp.text).group(0))
    print(f"[+] Got number {num1} from server")

    resp = s.get(URL)
    num2 = int(NUMBER_REGEX.search(resp.text).group(0))
    print(f"[+] Got second number {num2} from server")

    num1_lsb = num1 - 1000000
    num2_lsb = num2 - 1000000

    guess = []
    for i in range(256):
        possible = (i << 24) | num1_lsb
        state_s0 = reverse_xorshift32(possible)
        state_s2 = randgen_xorshift32(possible)

        print(f"state_s2: {state_s2}, num2_lsb: {num2_lsb}")
        if (state_s2 & 0xffffff) == num2_lsb:
            print(f"Matching internal state: {hex(possible)}")
            guess.append(possible)


    print(guess)
    state_s1 = guess[0]

    state_s2 = randgen_xorshift32(state_s1)
    state_s3 = randgen_xorshift32(state_s2)
    predict_lsb = state_s3 & 0xFFFFFF
    prediction = f"{predict_lsb + 1_000_000:08d}"

    # TODO: Guess the right lottory draw *somehow*

    resp = s.post(URL, data={"guess": prediction})
    number = NUMBER_REGEX.search(resp.text).group(0)
    print(f"[+] Server responsed with number {number}")
    if m := extract_flag_from_string(resp.text):
        print(f"[+] Flag: {m}")
    else:
        print("[+] No flag :'(")
        #print(resp.text)
