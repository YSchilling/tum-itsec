#!/usr/bin/env python3

import select
import socket
from server import  p, g
import asyncio
import hashlib
import hmac
import os
import secrets
import subprocess
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

SERVER = ("127.0.0.1", 1024) # For local testing, this may be useful
#SERVER = ("itsec.sec.in.tum.de", 7017)
PASSWORD = b"6564ce9e1f21472b"

def compute_mac(message):
    """Protect messages against manipulation"""
    return hmac.new(auth_key, message, digestmod="sha256").digest()

def kdf_aes(s):
    """Derive a key suitable for AES encryption/decryption from the negotiated DH secret"""
    h = hashlib.sha512()
    h.update(f"{s}".encode())
    return h.digest()[:16]

def encrypt(message, mac, key):
    """Computes the message's MAC, then encrypts both with AES-CBC according to the task description"""
    # You should probably avoid MAC-then-encrypt...
    iv = os.urandom(16)
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    return iv + cipher.encrypt(pad(message + mac, block_size=16))

def decrypt(message, key):
    iv, message = message[:16], message[16:]
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    message = cipher.decrypt(message)
    return unpad(message, block_size=16)

if __name__ == "__main__":
    with socket.socket() as side_a, socket.socket() as side_b:
        print("Connecting to party A")
        side_a.connect(SERVER)
        #side_a.recv(len("Password: "))
        #side_a.send(PASSWORD + b"\n")
        side_a.send(b"A\n")

        print("Connecting to party B")
        side_b.connect(SERVER)
        #side_b.recv(len("Password: "))
        #side_b.send(PASSWORD + b"\n")
        side_b.send(b"B\n")

        print("Connected successfully")

        side_a = side_a.makefile("rw")
        side_b = side_b.makefile("rw")

        c = 64
        C = pow(g, c, p)

        # DH for side_a
        A = int(side_a.readline().strip())
        side_a.write("{}\n".format(C))
        side_a.flush()
        sa = pow(A, c, p)
        key_a = kdf_aes(sa)
        print("key_a:", key_a.hex())

        # DH for side_b
        B = int(side_b.readline().strip())
        side_b.write("{}\n".format(C))
        side_b.flush()
        sb = pow(B, c, p)
        key_b = kdf_aes(sb)
        print("key_b:", key_b.hex())

        while side_a or side_b:
            if side_a:
                message_a = side_a.readline().strip()
                decrypted_message_a = decrypt(bytes.fromhex(message_a), key_a)
                raw_message_a = decrypted_message_a[:-32]
                mac = decrypted_message_a[-32:]
                print("Message A -> B:", raw_message_a)
                side_b.write("{}\n".format(encrypt(raw_message_a, mac, key_b).hex().encode() + b"\n"))
                side_b.flush()

            break
            if side_b:
                message_b = side_b.readline().strip()
                decrypted_message_b = decrypt(bytes.fromhex(message_b), key_b)
                raw_message_b = decrypted_message_b[:-32]
                mac = decrypted_message_b[-32:]
                print("Message B -> A:", raw_message_b)
                side_a.write("{}\n".format(encrypt(raw_message_b, mac, key_a)))
                side_a.flush()

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

