#!/usr/bin/env python3

import hashlib
import subprocess
import os
import asyncio
from fha256 import fha_init, fha_update, fha_final

def create_keyed_hash(secret, msg):
    h = fha_init()
    fha_update(h, secret)
    fha_update(h, msg)
    digest = fha_final(h)
    return digest

with open("secret-key.bin", "rb") as keyfile:
    secret = keyfile.read()
msg = b"http://www.bank.de/onlinebanking.html?lang=deutsch&is_admin=false"

async def handle_request(reader, writer):
    print("New connection")
    mac = create_keyed_hash(secret, msg)
    writer.write(f"{msg.hex()}\n{mac.hex()}\n".encode())
    await writer.drain()

    new_msg_hex = await reader.readline()
    new_msg_hex = new_msg_hex.strip().decode(errors='ignore')
    print("Message (hex):           ", new_msg_hex)
    new_mac_hex = await reader.readline()
    new_mac_hex = new_mac_hex.strip().decode(errors='ignore')
    print("User-supplied MAC (hex): ", new_mac_hex)

    new_msg = bytes.fromhex(new_msg_hex)
    check_mac_hex = create_keyed_hash(secret, new_msg).hex()
    print("Expected MAC (hex):      ", check_mac_hex)

    if b"is_admin=true" in new_msg and new_msg.startswith(msg) and check_mac_hex == new_mac_hex:
        flag = subprocess.check_output("/bin/flag")
        writer.write(flag)
    else:
        print("Nope...")
        writer.write(b"Sorry, but no :(")
    await writer.drain()
    writer.close()

async def run_server():
    server = await asyncio.start_server(handle_request, "0.0.0.0", 1024)
    print("Serving on {}".format(server.sockets[0].getsockname()))
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(run_server())
