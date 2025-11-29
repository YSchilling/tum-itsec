import socket
import re

# TODO: Password aus Taskbeschreibung einsetzen
PASSWORD = b"{{CODE}}"

def read_until(s, token):
    """Reads from socket `s` until a string `token` is found in the response of the server"""
    buf = b""
    while True:
        data = s.recv(1)
        buf += data
        if token in buf or not data:
            return buf

s = socket.socket()
s.connect(("itsec.sec.in.tum.de", 7011))
s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

# Read password prompt
read_until(s, b": ")
s.sendall(PASSWORD + b"\n")

start = read_until(s, b"Do you").decode()
print(f"Initial message from server:\n{start}\n")

msg, iv = re.match(r"I have an encrypted message for you:\n([0-9a-f]*) \(IV was ([0-9a-f]*)\)", start).groups()
iv = bytes.fromhex(iv)
msg = bytes.fromhex(msg)

# The server allows you to test the padding of multiple messages per connection.
# You have to send the IV and the encrypted message hexlified.
# If the padding is okay, the server will answer with b"OK!\n" or with an error message.

# Furthermore, the protocol is telnet compatible.
# Therefore, you can connect to the server using socat, nc or telnet.
# This will allow you to test the steps of your exploit manually before implementing them in Python.

# TODO: Implement padding oracle attack here by altering the code below

s.send(iv.hex().encode() + b"\n", socket.MSG_MORE)
s.send(msg.hex().encode() + b"\n")
response = read_until(s, b"\n")
print(response)
