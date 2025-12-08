#!/usr/bin/env python3

import hashlib
import select
import socket

# SERVER = ("127.0.0.1", 1024) # For local testing, this may be useful
SERVER = ("itsec.sec.in.tum.de", 7017)
PASSWORD = b"{{CODE}}"

def kdf_aes(s):
    """Derive a key suitable for AES encryption/decryption from the negotiated DH secret"""
    h = hashlib.sha512()
    h.update(f"{s}".encode())
    return h.digest()[:16]

if __name__ == "__main__":
    with socket.socket() as side_a, socket.socket() as side_b:
        print("Connecting to party A")
        side_a.connect(SERVER)
        side_a.recv(len("Password: "))
        side_a.send(PASSWORD + b"\n")
        side_a.send(b"A\n")

        print("Connecting to party B")
        side_b.connect(SERVER)
        side_b.recv(len("Password: "))
        side_b.send(PASSWORD + b"\n")
        side_b.send(b"B\n")

        print("Connected successfully")
        # This forwards all messages, you can delete this and use the commented-out
        # hints below (or just adjust this code if you prefer working with raw sockets)
        while True:
            sockets_with_data, _, _ = select.select([side_a, side_b], [], [])

            if side_a in sockets_with_data:
                buf = side_a.recv(1024)
                if buf == b"":
                    print("Party A closed connection")
                    break
                print("A -> B: {}".format(buf.strip().decode()))
                side_b.sendall(buf)
            if side_b in sockets_with_data:
                buf = side_b.recv(1024)
                if buf == b"":
                    print("Party B closed the connection")
                    break
                print("B -> A: {}".format(buf.strip().decode()))
                side_a.sendall(buf)

        # You may find these hints useful:
        #
        # Convert socket to file like class to get a readline method
        #    side_a = side_a.makefile("rw")
        #    side_b = side_b.makefile("rw")
        #
        # To read a message from party A, you can then use
        #    message = side_a.readline().strip()
        # and to forward it to party B
        #    side_b.write("{}\n".format(message))
        #    side_b.flush()

