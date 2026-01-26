import re
import socket

HOST = "itsec.sec.in.tum.de"
PORT = 7022

# Reads from the given socket until needle is found in the output or the connection closes,
# then returns all received bytes.
# The needle has to be given as a bytestring.
def recv_until(s, needle):
    buf = b""
    while needle not in buf:
        recv = s.recv(1)
        if not recv:
            return recv
        buf += recv
    return buf

# Returns only the flag if there is one in the passed string, otherwise returns None
def extract_flag_from_string(string):
    match = re.search(r'flag\{[^}]+}', string)
    if match:
        return match.group(0)
    return None

with socket.socket() as sock:
    sock.connect((HOST, PORT))
    # Receive password prompt ("Password: ") and discard it
    recv_until(sock, b": ")
    sock.send(b"{{CODE}}\n")

    # TODO implement exploit
    pass
