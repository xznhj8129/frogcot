"""Real-socket TCP/TLS transport checks without a mock transport."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import socket
import ssl
import subprocess
import tempfile
import threading
import unittest

from frogcot import PersistentCoTClient


FIRST = b'<event uid="first"><detail /></event>'
SECOND = b'<event uid="second"><detail /></event>'
REQUEST = b'<event uid="request"><detail /></event>'


def exchange(listener, release, context):
    connection, _ = listener.accept()
    if context is not None:
        connection = context.wrap_socket(connection, server_side=True)
    with connection:
        connection.settimeout(5)
        received = bytearray()
        while len(received) < len(REQUEST):
            received.extend(connection.recv(4096))
        if received != REQUEST:
            raise AssertionError(f'Unexpected payload: {received!r}')
        connection.sendall(FIRST[:12])
        if not release.wait(5):
            raise TimeoutError('Client did not release the fragmented event')
        connection.sendall(FIRST[12:] + SECOND)


class TCPTransportTest(unittest.TestCase):
    def test_plain_tcp_and_default_tls_use_the_same_framing(self):
        with tempfile.TemporaryDirectory() as directory:
            cert = Path(directory) / 'test.pem'
            key = Path(directory) / 'test.key'
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                '-keyout', str(key), '-out', str(cert), '-days', '1',
                '-subj', '/CN=localhost', '-addext', 'subjectAltName=DNS:localhost',
            ], check=True, capture_output=True)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert, key)
            context.load_verify_locations(cert)
            context.verify_mode = ssl.CERT_REQUIRED
            for tls in (False, True):
                with self.subTest(tls=tls), socket.socket() as listener:
                    listener.bind(('127.0.0.1', 0))
                    listener.listen()
                    listener.settimeout(5)
                    port = listener.getsockname()[1]
                    release = threading.Event()
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        server = executor.submit(exchange, listener, release, context if tls else None)
                        client = (
                            PersistentCoTClient('127.0.0.1', port, str(cert), str(cert), str(key), server_hostname='localhost')
                            if tls else PersistentCoTClient('127.0.0.1', port, tls=False)
                        )
                        try:
                            client.connect()
                            self.assertTrue(client.connected)
                            client.send(REQUEST)
                            self.assertIsNone(client.receive(0.05))
                            release.set()
                            self.assertEqual(client.receive(5), FIRST)
                            self.assertEqual(client.receive(5), SECOND)
                            with self.assertRaises(ConnectionError):
                                client.receive(5)
                            self.assertFalse(client.connected)
                            server.result(timeout=5)
                        finally:
                            release.set()
                            client.close()

    def test_tls_still_requires_certificates(self):
        with self.assertRaisesRegex(ValueError, 'TLS requires'):
            PersistentCoTClient('localhost', 8089)
        with self.assertRaisesRegex(ValueError, 'TCP does not use'):
            PersistentCoTClient('localhost', 8087, ca='unused.pem', tls=False)
