#!/usr/bin/env python3

import hashlib
import select
import socket
import collections

SERVER = ("itsec.sec.in.tum.de", 7018)
PASSWORD = b"{{CODE}}"

# For local testing, this may be useful. Also comment out password logic when testing locally.
# SERVER = ("127.0.0.1", 1024)

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

intercepted_message = collections.namedtuple('intercepted_message', ('direction', 'content'))
# Tells Bob (the client) to send the given message to Alice (the server).
# Alice will respond with that message and a flag.
# Returns a copy of all TLS messages exchanged between Alice and Bob.
def record_exchange(s, bobs_message):
    recv_until(s, b"Please type your message: ")
    s.send(bobs_message + b"\n")
    messages = []
    while True:
        line = recv_until(s, b"\n").decode()
        if line == "---END---\n":
            break
        split = line.split(":")
        messages.append(intercepted_message(split[0], bytes.fromhex(split[1])))
    return messages

def pwn(s):
    messages = record_exchange(s, b"Hi Alice, I'm Bob!")
    for msg in messages:
        print(f"Intercepted message: direction {msg.direction}, content (hex) {msg.content.hex()}")
    # TODO implement exploit

def main():
    with socket.socket() as s:
        s.connect(SERVER)
        recv_until(s, b"Password: ")
        s.send(PASSWORD + b"\n")
        print("Connected successfully")
        pwn(s)

if __name__ == "__main__":
    main()
