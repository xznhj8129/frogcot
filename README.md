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

CoTtypes.xml from https://github.com/Esri/defense-solutions-proofs-of-concept/

Todo: 
Converts XSD to Pydantic using xsdata
XSD Schemas from ATAK
Fixed two typos
    xsd/events/point.xsd
    xsd/detail/__geofence.xsd
(OR NOT: this has been the bane of my existence)
Check this out instead https://github.com/dfpc-coe/node-CoT
