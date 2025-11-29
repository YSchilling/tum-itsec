from fha256 import fha_init, fha_update, fha_final
import hashlib
import struct
import math
import sys
import socket

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

def forge_keyed_hash(orig_msg, orig_mac, append):
    # TODO: Message new_msg und new_mac erzeugen, sodass msg != new_msg, aber new_mac gültig.
    # MAC_k(msg) := FHA(k || msg)
    # keysize := len(k)

    # TODO: Da k nur auf dem Server bekannt ist, muss keysize anders bestimmt werden.
    keysize = 0

    # TODO: new_msg bestimmen
    new_msg = b""

    # TODO: passenden MAC new_mac zu new_msg bestimmen
    m = fha_init()
    m["count_lo"] = 0 # TODO: Länge der Nachricht bis hier (in Bits)
    m['digest'] = list(struct.unpack(">IIIIIIII", orig_mac))
    # Beispiel zum "weiter hashen":
    #   fha_update(m, b"Hello")
    new_mac = fha_final(m)

    return (new_msg, new_mac)

# Beispiel für die Erstellung eines FHA hashes mit fha_init(),
# fha_update() und fha_final()
def hash_using_fha(msg):
    """Create a regular FHA hash of a message"""
    m = fha_init()
    fha_update(m, msg)
    return fha_final(m)

def unhex(x):
    return bytes.fromhex(x.decode().strip())

# Verbindung zum Server herstellen und Passwort senden
s = socket.socket()
s.connect(("itsec.sec.in.tum.de", 7014))
read_until(s, b"Password: ")
s.sendall(PASSWORD + b"\n")

# Message msg vom Server holen
msg_hex = read_until(s, b"\n")
msg = unhex(msg_hex)
# MAC_k(msg) vom Server holen
mac_hex = read_until(s, b"\n")
mac = unhex(mac_hex)
print("Got message from server:", msg)
print("MAC for this message (hex):", mac_hex)

print("Generating message with is_admin=true...")

new_msg, new_mac = forge_keyed_hash(msg, mac, b"is_admin=true")

# new_msg und new_mac zum Server für Prüfung schicken
s.sendall(new_msg.hex().encode() + b"\n")
s.sendall(new_mac.hex().encode() + b"\n")

# Flagge ausgeben
print(read_until(s, b"\n"))
