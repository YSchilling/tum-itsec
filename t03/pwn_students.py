import re
import socket

HOST = "itsec.sec.in.tum.de"
PORT = 7003

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
    sock.send(b"ea13c58cc32b9856\n")
    response = recv_until(sock, b"\n")
    response_str = response[:-3]
    result = "".join(chr(int(response_str[i:i+2], 16))
        for i in range(0, len(response_str), 2))
    print(extract_flag_from_string(result))