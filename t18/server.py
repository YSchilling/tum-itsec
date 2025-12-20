#!/usr/bin/python3 -u

import collections
import gzip
import io
import os
import queue
import select
import socket
import socketserver
import ssl
import subprocess
import sys
import threading
import time

# First, grab the certificates
assert os.path.exists('cert.pem') and os.path.exists('key.pem'), 'SSL certificate and/or key not found'

server_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
server_ctx.load_cert_chain('cert.pem', 'key.pem')

# Disable verification (we don't want to require you to have a real hostname to use for this)
client_ctx = ssl.create_default_context()
client_ctx.check_hostname = False
client_ctx.verify_mode = ssl.VerifyMode.CERT_NONE

# Turn this on only if you think you broke something, this produces _a lot_ of output
VERBOSE = False

# Log to stderr by default, but serialize output first so we don't get everything mangled by the threads
def log(*args, **kwargs):
    with io.StringIO() as output:
        print(*args, **kwargs, file=output)
        sys.stderr.write(output.getvalue())
        sys.stderr.flush()
def verbose(*args, **kwargs):
    if VERBOSE:
        log(*args, **kwargs)

# The man-in-the-middle that grabs all the messages
mitm_state = collections.namedtuple('mitm_state', ('label', 'forward_to'))

def mitm(connection_id, sending, socket_queue):
    log(f'{connection_id}: MitM thread started')
    while True:
        sockets = socket_queue.get()
        if sockets is None:
            break

        # Got a pair of sockets we can intercept data on
        socket_alice, socket_bob, done_flag = sockets
        verbose(f'{connection_id}: MitM thread received socket pair')
        try:
            info = {
                socket_alice: mitm_state(label='S -> C', forward_to=socket_bob),
                socket_bob:   mitm_state(label='C -> S', forward_to=socket_alice)
            }
            while not done_flag.is_set():
                readable, _, _ = select.select([socket_alice, socket_bob], [], [], 0.5)
                for mitm_socket in readable:
                    state = info[mitm_socket]
                    # Read data from the socket
                    data = mitm_socket.recv(1024)
                    if not data:
                        continue
                    sending.write(f'{state.label}: {data.hex()}\n'.encode())
                    verbose(f'{connection_id}: {state.label}: {data.hex()}')
                    # Forward the intercepted data
                    state.forward_to.sendall(data)
        except BrokenPipeError:
            log(f'{connection_id}: MitM failed to send intercepted message (client disconnected)')
        finally:
            socket_alice.close()
            socket_bob.close()
            verbose(f'{connection_id}: MitM thread done with this socket pair')
    log(f'{connection_id}: MitM thread done')

# "The server" a.k.a. Alice
def server(connection_id, response, socket_queue):
    log(f'{connection_id}: Server thread started')
    while True:
        raw_socket = socket_queue.get()
        if raw_socket is None:
            break

        verbose(f'{connection_id}: Server received socket')
        wrapped_socket = None
        # Got a pair of sockets we can intercept data on
        try:
            wrapped_socket = server_ctx.wrap_socket(raw_socket, server_side=True)
            bobs_message = wrapped_socket.recv(2048)
            verbose(f'{connection_id}: Server received {bobs_message}')
            # Send Alice's preconfigured response together with Bobs message back to Bob.
            # Also, let's save some bandwidth.
            wrapped_socket.sendall(gzip.compress(response + bobs_message))
        except (ssl.SSLEOFError, ssl.SSLZeroReturnError, ConnectionResetError):
            # This happens e.g. if the client disconnects early
            log(f'{connection_id}: Server received unexpected EOF')
        finally:
            if wrapped_socket:
                wrapped_socket.close()
            else:
                raw_socket.close()
            verbose(f'{connection_id}: Server done with this socket')
    log(f'{connection_id}: Server done')

# Handles an incoming client
def client_handler(receiving, sending, address=None):
    connection_id = f'{time.strftime("%FT%T%z")}-{os.urandom(4).hex()}'
    alice = mitm_alice = mitm_bob = bob = None
    try:
        prefix = b"This is some random text I typed here. Your flag is: "
        flag = subprocess.check_output('/bin/flag').strip()
        log(f'{connection_id}: newly received{f" from {address}" if address else ""}')
        log(f'{connection_id}: Flag is {flag.decode()}')

        # What Alice will respond with:
        alice_response = prefix + flag

        # Spin up a thread that handles the snooping
        sockets_to_mitm = queue.Queue()
        mitm_thread = threading.Thread(target=mitm, args=(connection_id, sending, sockets_to_mitm))
        mitm_thread.start()

        # Spin up the server (Alice) that responds to Bob's messages
        sockets_to_alice = queue.Queue()
        server_thread = threading.Thread(target=server, args=(connection_id, alice_response, sockets_to_alice))
        server_thread.start()

        # Avoid doing a complete TLS handshake for every message
        last_session = None

        while True:
            sending.write(b'Please type your message: ')
            attacker_data = receiving.readline().rstrip(b'\n')
            if len(attacker_data) > 1024:
                sending.write(b'That\'s a bit too long, sorry...\n')
                # TODO EXIT
            if attacker_data == b'':
                sending.write(b'You didn\'t give me a message...\n')
                # TODO EXIT

            # Make a MitM'd connection
            alice, mitm_alice = socket.socketpair()
            mitm_bob, bob = socket.socketpair()

            # Give connection information to the snooper, and to Alice
            single_connection_done = threading.Event()
            sockets_to_mitm.put((mitm_alice, mitm_bob, single_connection_done))
            sockets_to_alice.put(alice)

            # Wrap Bob's socket to send SSL/TLS.
            secure_bob = client_ctx.wrap_socket(bob, do_handshake_on_connect=False)
            if last_session is not None:
                secure_bob.session = last_session
            secure_bob.do_handshake()

            # Main part! Send data as Bob to Alice, and wait for Alice's answer
            verbose(f'Sending {attacker_data} to Alice')
            secure_bob.send(attacker_data)
            response = secure_bob.recv(1024)
            verbose(f'Received {gzip.decompress(response)} from Alice')

            # Tell the MitM thread to expect a new set of sockets, and clean up Bob's socket
            single_connection_done.set()
            last_session = secure_bob.session
            secure_bob.close()

            # Signal end-of-data
            sending.write(b'---END---\n')
    except (BrokenPipeError, ConnectionResetError, ssl.SSLEOFError, ssl.SSLZeroReturnError):
        log(f'{connection_id}: Client disconnected')
    except socket.timeout:
        try:
            sending.write(b'Please don\'t wait so long, I don\'t have all day...\n')
        except:
            pass # If that doesn't make it through for some reason, we don't care.
        log(f'{connection_id}: Client timed out')
    finally:
        sockets_to_mitm.put(None)
        sockets_to_alice.put(None)
        if single_connection_done:
            single_connection_done.set()
        server_thread.join()
        mitm_thread.join()
        # Try closing all the sockets again, for good measure
        if alice:
            alice.close()
        if mitm_alice:
            mitm_alice.close()
        if mitm_bob:
            mitm_bob.close()
        if bob:
            bob.close()
        log(f'{connection_id}: Done')

class ClientHandler(socketserver.BaseRequestHandler):
    def handle(self):
        s = self.request
        s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        client_handler(s.makefile('rb', buffering=0), s.makefile('wb', buffering=0), self.client_address)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    with ThreadedTCPServer(("0.0.0.0", 1024), ClientHandler) as tcpserver:
        tcpserver.serve_forever()
