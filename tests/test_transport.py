import unittest
from unittest import mock

from frogcot import PersistentCoTClient


class FakeSocket:
    def __init__(self, chunks=()):
        self.chunks = list(chunks)
        self.sent = []
        self.closed = False

    def recv(self, size):
        return self.chunks.pop(0)

    def pending(self):
        return 0

    def sendall(self, payload):
        self.sent.append(payload)

    def close(self):
        self.closed = True


class PersistentCoTClientTest(unittest.TestCase):
    def make_client(self, fake_socket):
        client = PersistentCoTClient(
            "tak.example",
            8089,
            "ca.pem",
            "client.pem",
            "client.key",
        )
        client._socket = fake_socket
        return client

    @mock.patch("frogcot.transport.socket.create_connection")
    @mock.patch("frogcot.transport.ssl.create_default_context")
    def test_connect_configures_one_tls_socket(
        self, create_context_mock, create_connection_mock
    ):
        raw_socket = FakeSocket()
        tls_socket = FakeSocket()
        context = create_context_mock.return_value
        context.wrap_socket.return_value = tls_socket
        create_connection_mock.return_value = raw_socket
        client = PersistentCoTClient(
            "tak.example",
            8089,
            "ca.pem",
            "client.pem",
            "client.key",
        )

        client.connect()

        create_context_mock.assert_called_once_with(
            mock.ANY,
            cafile="ca.pem",
        )
        context.load_cert_chain.assert_called_once_with(
            certfile="client.pem",
            keyfile="client.key",
        )
        create_connection_mock.assert_called_once_with(("tak.example", 8089))
        context.wrap_socket.assert_called_once_with(
            raw_socket,
            server_hostname="tak.example",
        )
        self.assertTrue(client.connected)

        with self.assertRaises(RuntimeError):
            client.connect()

        client.close()
        self.assertTrue(tls_socket.closed)

    @mock.patch("frogcot.transport.select.select")
    def test_receive_frames_split_and_concatenated_events(self, select_mock):
        first = b'<event uid="one"><detail><remarks>hello</remarks></detail></event>'
        second = b'<event uid="two">\n<point lat="1" />\n</event>'
        fake_socket = FakeSocket(
            [
                b"ignored preamble<ev",
                b"ent uid=\"one\"><detail><remarks>hello</remarks>",
                b"</detail></event>" + second,
            ]
        )
        client = self.make_client(fake_socket)
        select_mock.side_effect = lambda readers, _writers, _errors, _timeout: (
            readers,
            [],
            [],
        )

        self.assertEqual(client.receive(1.0), first)
        calls_after_first_event = select_mock.call_count
        self.assertEqual(client.receive(1.0), second)
        self.assertEqual(select_mock.call_count, calls_after_first_event)

    @mock.patch("frogcot.transport.select.select")
    def test_receive_retains_partial_event_across_timeout(self, select_mock):
        fake_socket = FakeSocket([b'<event uid="one">', b"</event>"])
        client = self.make_client(fake_socket)
        select_mock.side_effect = [
            ([fake_socket], [], []),
            ([], [], []),
            ([fake_socket], [], []),
        ]

        self.assertIsNone(client.receive(0.1))
        self.assertEqual(client.receive(0.1), b'<event uid="one"></event>')

    @mock.patch("frogcot.transport.select.select")
    def test_receive_closes_on_eof(self, select_mock):
        fake_socket = FakeSocket([b""])
        client = self.make_client(fake_socket)
        select_mock.return_value = ([fake_socket], [], [])

        with self.assertRaises(ConnectionError):
            client.receive(1.0)

        self.assertTrue(fake_socket.closed)
        self.assertFalse(client.connected)

    def test_send_uses_existing_socket(self):
        fake_socket = FakeSocket()
        client = self.make_client(fake_socket)
        event = b'<event uid="one"></event>'

        client.send(event)

        self.assertEqual(fake_socket.sent, [event])

    def test_send_requires_bytes_and_connection(self):
        fake_socket = FakeSocket()
        client = self.make_client(fake_socket)

        with self.assertRaises(TypeError):
            client.send("<event></event>")

        client.close()
        with self.assertRaises(RuntimeError):
            client.send(b"<event></event>")


if __name__ == "__main__":
    unittest.main()
