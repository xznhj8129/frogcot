"""Persistent TCP/TLS transport for Cursor-on-Target event streams."""

from collections import deque
import re
import select
import socket
import ssl
import time
from typing import Deque, Optional


_EVENT_START = re.compile(br"<event(?=[\s>])")
_EVENT_END = re.compile(br"</event\s*>")


class PersistentCoTClient:
    """Send and receive CoT XML over a single persistent TCP or TLS connection."""

    def __init__(
        self,
        host: str,
        port: int,
        ca: Optional[str] = None,
        client_certificate: Optional[str] = None,
        client_key: Optional[str] = None,
        server_hostname: Optional[str] = None,
        connect_timeout: Optional[float] = None,
        *,
        tls: bool = True,
    ):
        if tls and not all((ca, client_certificate, client_key)):
            raise ValueError("TLS requires ca, client_certificate, and client_key")
        if not tls and any((ca, client_certificate, client_key)):
            raise ValueError("TCP does not use TLS certificates")
        self.tls = tls
        self.host = host
        self.port = port
        self.ca = ca
        self.client_certificate = client_certificate
        self.client_key = client_key
        self.server_hostname = host if server_hostname is None else server_hostname
        self.connect_timeout = connect_timeout
        self._socket: Optional[socket.socket] = None
        self._buffer = bytearray()
        self._events: Deque[bytes] = deque()

    @property
    def connected(self) -> bool:
        """Whether this client currently owns a connected socket."""
        return self._socket is not None

    def connect(self) -> None:
        """Open the client's single connection; authenticate it when TLS is enabled."""
        if self._socket is not None:
            raise RuntimeError("PersistentCoTClient is already connected")

        context = None
        if self.tls:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.ca)
            context.load_cert_chain(
                certfile=self.client_certificate,
                keyfile=self.client_key,
            )

        raw_socket = socket.create_connection(
            (self.host, self.port), timeout=self.connect_timeout
        )
        try:
            connected_socket = (
                context.wrap_socket(raw_socket, server_hostname=self.server_hostname)
                if context is not None else raw_socket
            )
        except BaseException:
            raw_socket.close()
            raise

        self._socket = connected_socket
        self._buffer.clear()
        self._events.clear()

    def close(self) -> None:
        """Close the connection. Calling close more than once is safe."""
        connected_socket = self._socket
        self._socket = None
        if connected_socket is not None:
            connected_socket.close()

    def send(self, xml: bytes) -> None:
        """Send one XML byte payload on the existing connection."""
        if not isinstance(xml, bytes):
            raise TypeError("xml must be bytes")
        self._require_socket().sendall(xml)

    def receive(self, timeout: Optional[float]) -> Optional[bytes]:
        """Return the next complete CoT event, or ``None`` on timeout.

        Received data is retained across calls, allowing event boundaries to
        fall anywhere within socket receive chunks.
        """
        if timeout is not None and timeout < 0:
            raise ValueError("timeout must be non-negative or None")

        connected_socket = self._require_socket()
        if self._events:
            return self._events.popleft()

        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            remaining = (
                None if deadline is None else max(0.0, deadline - time.monotonic())
            )
            if isinstance(connected_socket, ssl.SSLSocket) and connected_socket.pending():
                readable = [connected_socket]
            else:
                readable, _, _ = select.select([connected_socket], [], [], remaining)
            if not readable:
                return None

            try:
                chunk = connected_socket.recv(65536)
            except TimeoutError:
                # The connect timeout may still be attached to the socket.
                # An idle read satisfies receive()'s documented timeout
                # contract; it is not a broken TAK connection.
                return None
            if not chunk:
                self.close()
                raise ConnectionError("CoT connection closed by peer")

            self._frame_events(chunk)
            if self._events:
                return self._events.popleft()

    def _require_socket(self) -> socket.socket:
        if self._socket is None:
            raise RuntimeError("PersistentCoTClient is not connected")
        return self._socket

    def _frame_events(self, chunk: bytes) -> None:
        self._buffer.extend(chunk)

        while True:
            start = _EVENT_START.search(self._buffer)
            if start is None:
                # Retain only enough bytes to recognize a start marker split
                # across the next receive boundary.
                del self._buffer[: max(0, len(self._buffer) - len(b"<event") + 1)]
                return

            if start.start():
                del self._buffer[: start.start()]

            end = _EVENT_END.search(self._buffer, start.end() - start.start())
            if end is None:
                return

            event_end = end.end()
            self._events.append(bytes(self._buffer[:event_end]))
            del self._buffer[:event_end]
