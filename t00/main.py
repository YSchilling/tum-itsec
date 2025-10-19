import requests

with requests.Session() as sess:
    target_url = "https://t00-bb71607a551c3925.itsec.sec.in.tum.de"
    response = sess.get(target_url)
    print(response.text)