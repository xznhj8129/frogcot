# frogcot
CoT Library

## Persistent TLS transport

`PersistentCoTClient` keeps one mutually authenticated TLS connection open. Its
`receive(timeout)` method uses `select` and returns a complete CoT `<event>` as
bytes as soon as one is available, or `None` when the timeout expires.

```python
from frogcot import PersistentCoTClient

client = PersistentCoTClient(
    "tak.example", 8089, "ca.pem", "client.pem", "client.key"
)
client.connect()
client.send(b'<event version="2.0" uid="example"></event>')
event = client.receive(timeout=1.0)
client.close()
```

## Live situational awareness

`SituationalAwareness` ingests one CoT `<event>` at a time and keeps the latest
PLI contacts and point markers by UID. GeoChat messages are retained in arrival
order. The parser and built-in WGS-84 range/bearing calculation use only the
Python standard library.

```python
from frogcot import GeoPoint, SituationalAwareness

state = SituationalAwareness()

# Pass each complete event returned by a transport receive loop.
state.ingest(pli_xml)
state.ingest(marker_xml)
state.ingest(geochat_xml)

contact = state.get_contact("RAVEN 1")       # UID or exact callsign, case-insensitive
marker = state.get_marker("objective alpha")
nearest = state.nearest_marker(contact)
solution = state.range_bearing(contact, marker)

print(nearest.callsign)
print(solution.range_m, solution.bearing_deg)  # metres, degrees true
print(state.chats[-1].sender, state.chats[-1].room, state.chats[-1].text)

# Coordinates can also be supplied directly as GeoPoint or (latitude, longitude).
from_here = state.range_bearing(GeoPoint(36.5165, -79.38), marker)
```

PLI types beginning with `a-f-G` are contacts. GeoChat type `b-t-f` is parsed
before marker classification; any other event carrying a `<point>` is retained
as a marker. `list_markers()` returns a snapshot of current marker state.

CoTtypes.xml from https://github.com/Esri/defense-solutions-proofs-of-concept/

Todo: 
Converts XSD to Pydantic using xsdata
XSD Schemas from ATAK
Fixed two typos
    xsd/events/point.xsd
    xsd/detail/__geofence.xsd
(OR NOT: this has been the bane of my existence)
Check this out instead https://github.com/dfpc-coe/node-CoT
