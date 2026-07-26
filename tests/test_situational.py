import datetime
import unittest

import frogcot


PLI = b"""\
<event version="2.0" uid="ANDROID-pli-1" type="a-f-G-U-C"
       time="2026-07-26T14:00:00.000Z"
       start="2026-07-26T14:00:00.000Z"
       stale="2026-07-26T14:01:00.000Z" how="m-g">
  <point lat="36.5165" lon="-79.3832" hae="112.5" ce="4.0" le="6.0"/>
  <detail>
    <contact callsign="Raven 1" endpoint="192.0.2.1:4242:tcp"/>
    <uid Droid="Raven 1"/>
    <__group name="Cyan" role="Team Lead"/>
  </detail>
</event>
"""

HOSTILE_MARKER = b"""\
<event version="2.0" uid="marker-hostile" type="a-h-G"
       time="2026-07-26T14:00:10Z"
       start="2026-07-26T14:00:10Z"
       stale="2026-07-26T15:00:10Z" how="h-g-i-g-o">
  <point lat="36.5166" lon="-79.3900" hae="100" ce="10" le="10"/>
  <detail><contact callsign="Objective ALPHA"/></detail>
</event>
"""

UNKNOWN_MARKER = b"""\
<event version="2.0" uid="marker-unknown" type="a-u-G"
       time="2026-07-26T14:00:11Z"
       start="2026-07-26T14:00:11Z"
       stale="2026-07-26T15:00:11Z" how="h-g-i-g-o">
  <point lat="36.5170" lon="-79.4000" hae="90" ce="12" le="12"/>
  <detail><contact callsign="Unknown One"/></detail>
</event>
"""

OTHER_POINT_EVENT = b"""\
<event version="2.0" uid="sensor-point" type="b-m-p-s-p-loc"
       time="2026-07-26T14:00:12+00:00"
       start="2026-07-26T14:00:12Z"
       stale="2026-07-26T15:00:12Z" how="m-g">
  <point lat="36.5171" lon="-79.4100" hae="80" ce="15" le="15"/>
  <detail><contact callsign="Camera 2"/></detail>
</event>
"""

ROOM_GEOCHAT = b"""\
<event version="2.0"
       uid="GeoChat.ANDROID-pli-1.All Chat Rooms.room-message"
       type="b-t-f" time="2026-07-26T14:01:00Z"
       start="2026-07-26T14:01:00Z"
       stale="2026-07-27T14:01:00Z" how="h-g-i-g-o">
  <point lat="36.5165" lon="-79.3832" hae="112.5" ce="4" le="6"/>
  <detail>
    <__chat parent="TeamGroups" groupOwner="false" messageId="room-message"
            chatroom="All Chat Rooms" id="All Chat Rooms"
            senderCallsign="Raven 1">
      <chatgrp uid0="ANDROID-pli-1" uid1="All Chat Rooms"
               id="All Chat Rooms"/>
    </__chat>
    <remarks source="BAO.F.ATAK.ANDROID-pli-1"
             time="2026-07-26T14:01:00Z">Room check-in</remarks>
  </detail>
</event>
"""

DIRECT_GEOCHAT = b"""\
<event version="2.0"
       uid="GeoChat.ANDROID-pli-2.ANDROID-pli-1.direct-message"
       type="b-t-f" time="2026-07-26T14:02:00Z"
       start="2026-07-26T14:02:00Z"
       stale="2026-07-27T14:02:00Z" how="h-g-i-g-o">
  <detail>
    <__chat parent="RootContactGroup" groupOwner="false"
            messageId="direct-message" chatroom="Raven 1"
            id="ANDROID-pli-1" senderCallsign="Viper 2">
      <chatgrp uid0="ANDROID-pli-2" uid1="ANDROID-pli-1"
               id="ANDROID-pli-1"/>
    </__chat>
    <remarks source="BAO.F.ATAK.ANDROID-pli-2"
             to="ANDROID-pli-1"
             time="2026-07-26T14:02:00Z">Direct message</remarks>
  </detail>
</event>
"""


class SituationalAwarenessTest(unittest.TestCase):
    def setUp(self):
        self.state = frogcot.SituationalAwareness()

    def test_ingests_typed_pli_and_preserves_fields(self):
        contact = self.state.ingest(PLI)

        self.assertIsInstance(contact, frogcot.Contact)
        self.assertEqual(contact.uid, "ANDROID-pli-1")
        self.assertEqual(contact.cot_type, "a-f-G-U-C")
        self.assertEqual(contact.callsign, "Raven 1")
        self.assertEqual(
            contact.time,
            datetime.datetime(
                2026, 7, 26, 14, 0, tzinfo=datetime.timezone.utc
            ),
        )
        self.assertEqual(contact.point.latitude, 36.5165)
        self.assertEqual(contact.point.longitude, -79.3832)
        self.assertEqual(contact.point.hae, 112.5)
        self.assertEqual(contact.point.ce, 4.0)
        self.assertEqual(contact.point.le, 6.0)
        self.assertEqual(self.state.contacts, [contact])

    def test_pli_state_keeps_latest_event_by_cot_time(self):
        original = self.state.ingest(PLI)
        newer = PLI.replace(
            b'lat="36.5165"', b'lat="36.5200"'
        ).replace(
            b"2026-07-26T14:00:00.000Z", b"2026-07-26T14:05:00.000Z"
        )
        older = PLI.replace(
            b'lat="36.5165"', b'lat="42.0000"'
        ).replace(
            b"2026-07-26T14:00:00.000Z", b"2026-07-26T13:55:00.000Z"
        )

        latest = self.state.ingest(newer)
        self.state.ingest(older)

        self.assertNotEqual(original, latest)
        self.assertEqual(
            self.state.get_contact("ANDROID-pli-1").point.latitude, 36.5200
        )

    def test_ingests_named_marker_types_and_other_point_events(self):
        hostile = self.state.ingest(HOSTILE_MARKER)
        unknown = self.state.ingest(UNKNOWN_MARKER)
        sensor = self.state.ingest(OTHER_POINT_EVENT)

        self.assertIsInstance(hostile, frogcot.Marker)
        self.assertIsInstance(unknown, frogcot.Marker)
        self.assertIsInstance(sensor, frogcot.Marker)
        self.assertEqual(
            [item.uid for item in self.state.list_markers()],
            ["marker-hostile", "marker-unknown", "sensor-point"],
        )
        self.assertEqual(sensor.callsign, "Camera 2")

    def test_uid_and_callsign_resolution_is_case_insensitive_exact_first(self):
        self.state.ingest(PLI)
        self.state.ingest(HOSTILE_MARKER)
        case_variant = HOSTILE_MARKER.replace(
            b'marker-hostile', b'marker-case'
        ).replace(
            b'Objective ALPHA', b'objective alpha'
        ).replace(
            b"2026-07-26T14:00:10Z", b"2026-07-26T14:00:20Z"
        )
        self.state.ingest(case_variant)

        self.assertEqual(
            self.state.get_contact("ANDROID-pli-1").callsign, "Raven 1"
        )
        self.assertEqual(self.state.get_contact("rAvEn 1").uid, "ANDROID-pli-1")
        self.assertEqual(
            self.state.get_marker("Objective ALPHA").uid, "marker-hostile"
        )
        self.assertEqual(
            self.state.get_marker("OBJECTIVE ALPHA").uid, "marker-case"
        )
        self.assertIsNone(self.state.get_marker("Objective"))

    def test_ingests_room_and_direct_geochat(self):
        room = self.state.ingest(ROOM_GEOCHAT)
        direct = self.state.ingest(DIRECT_GEOCHAT)

        self.assertIsInstance(room, frogcot.GeoChat)
        self.assertEqual(room.sender, "Raven 1")
        self.assertEqual(room.room, "All Chat Rooms")
        self.assertEqual(room.text, "Room check-in")
        self.assertEqual(room.point.latitude, 36.5165)
        self.assertEqual(direct.sender, "Viper 2")
        self.assertEqual(direct.room, "Raven 1")
        self.assertEqual(direct.text, "Direct message")
        self.assertIsNone(direct.point)
        self.assertEqual(self.state.chats, [room, direct])
        self.assertEqual(self.state.list_markers(), [])

    def test_range_bearing_and_nearest_marker(self):
        origin = frogcot.GeoPoint(0.0, 0.0)
        due_east = frogcot.GeoPoint(0.0, 1.0)
        result = self.state.range_bearing(origin, due_east)

        self.assertAlmostEqual(result.range_m, 111319.49, delta=0.5)
        self.assertAlmostEqual(result.bearing_deg, 90.0, delta=0.001)
        self.assertEqual(
            self.state.range_bearing((0.0, 0.0), (1.0, 0.0)).bearing_deg,
            0.0,
        )

        self.state.ingest(PLI)
        self.state.ingest(HOSTILE_MARKER)
        self.state.ingest(UNKNOWN_MARKER)
        self.assertEqual(
            self.state.nearest_marker("raven 1").uid, "marker-hostile"
        )
        named_result = self.state.range_bearing(
            "Raven 1", "Objective ALPHA"
        )
        self.assertGreater(named_result.range_m, 800.0)
        self.assertLess(named_result.range_m, 1000.0)

    def test_unrecognized_non_point_event_is_not_retained(self):
        event = b"""\
        <event uid="status-1" type="t-x-c-t"
          time="2026-07-26T14:00:00Z"><detail/></event>"""

        self.assertIsNone(self.state.ingest(event))
        self.assertEqual(self.state.contacts, [])
        self.assertEqual(self.state.list_markers(), [])

    def test_rejects_malformed_or_multiple_event_documents(self):
        with self.assertRaises(frogcot.CoTParseError):
            self.state.ingest(b"<detail/>")
        with self.assertRaises(frogcot.CoTParseError):
            self.state.ingest(b"<event/><event/>")
        with self.assertRaises(frogcot.CoTParseError):
            self.state.ingest(
                b'<event uid="bad" type="a-h-G" time="not-a-time">'
                b'<point lat="0" lon="0"/></event>'
            )

    def test_public_types_are_exported_from_package(self):
        for name in (
            "CoTParseError",
            "Contact",
            "GeoChat",
            "GeoPoint",
            "Marker",
            "RangeBearing",
            "SituationalAwareness",
        ):
            self.assertIsNotNone(getattr(frogcot, name))


if __name__ == "__main__":
    unittest.main()
