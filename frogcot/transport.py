"""Persistent TLS transport for Cursor-on-Target event streams."""

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
    """Send and receive CoT XML over a single persistent TLS connection."""

    def __init__(
        self,
        host: str,
        port: int,
        ca: str,
        client_certificate: str,
        client_key: str,
        server_hostname: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.ca = ca
        self.client_certificate = client_certificate
        self.client_key = client_key
        self.server_hostname = host if server_hostname is None else server_hostname
        self._socket: Optional[ssl.SSLSocket] = None
        self._buffer = bytearray()
        self._events: Deque[bytes] = deque()

    @property
    def connected(self) -> bool:
        """Whether this client currently owns a connected TLS socket."""
        return self._socket is not None

    def connect(self) -> None:
        """Open and authenticate the client's single TLS connection."""
        if self._socket is not None:
            raise RuntimeError("PersistentCoTClient is already connected")

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.ca)
        context.load_cert_chain(
            certfile=self.client_certificate,
            keyfile=self.client_key,
        )

        raw_socket = socket.create_connection((self.host, self.port))
        try:
            tls_socket = context.wrap_socket(
                raw_socket,
                server_hostname=self.server_hostname,
            )
        except BaseException:
            raw_socket.close()
            raise

        self._socket = tls_socket
        self._buffer.clear()
        self._events.clear()

    def close(self) -> None:
        """Close the connection. Calling close more than once is safe."""
        tls_socket = self._socket
        self._socket = None
        if tls_socket is not None:
            tls_socket.close()

    def send(self, xml: bytes) -> None:
        """Send one XML byte payload on the existing connection."""
        if not isinstance(xml, bytes):
            raise TypeError("xml must be bytes")
        self._require_socket().sendall(xml)

    def receive(self, timeout: Optional[float]) -> Optional[bytes]:
        """Return the next complete CoT event, or ``None`` on timeout.

        Received data is retained across calls, allowing event boundaries to
        fall anywhere within TLS receive chunks.
        """
        if timeout is not None and timeout < 0:
            raise ValueError("timeout must be non-negative or None")

        tls_socket = self._require_socket()
        if self._events:
            return self._events.popleft()

        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            remaining = (
                None if deadline is None else max(0.0, deadline - time.monotonic())
            )
            if tls_socket.pending():
                readable = [tls_socket]
            else:
                readable, _, _ = select.select([tls_socket], [], [], remaining)
            if not readable:
                return None

            chunk = tls_socket.recv(65536)
            if not chunk:
                self.close()
                raise ConnectionError("CoT TLS connection closed by peer")

            self._frame_events(chunk)
            if self._events:
                return self._events.popleft()

    def _require_socket(self) -> ssl.SSLSocket:
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
