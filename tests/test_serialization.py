import re
import unittest
import xml.etree.ElementTree as ET

import frogcot


class SerializationTest(unittest.TestCase):
    COT_TIME_PATTERN = re.compile(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$"
    )

    def test_geochat_and_marker(self):
        client = frogcot.ATAKClient("sender")
        position = {"lat": 1, "lon": 2, "alt": 3, "ce": 4, "le": 5}

        geochat = ET.fromstring(
            client.geochat("hello", to_team="team", pos=position)
        )
        marker = ET.fromstring(
            client.cot_marker("marker", "marker-1", "a-f-G", position)
        )

        self.assertTrue(geochat.get("uid").startswith("GeoChat."))
        self.assertEqual(geochat.findtext("./detail/remarks"), "hello")
        self.assertEqual(marker.get("uid"), "marker-1")
        self.assertEqual(marker.find("./detail/contact").get("callsign"), "marker")
        for event in (geochat, marker):
            for attribute in ("time", "start", "stale"):
                self.assertRegex(event.get(attribute), self.COT_TIME_PATTERN)

    def test_marker_has_atak_detail_fields_without_pli_metadata(self):
        client = frogcot.ATAKClient("sender")
        position = {"lat": 1, "lon": 2, "alt": 3, "ce": 4, "le": 5}

        marker = ET.fromstring(
            client.cot_marker(
                "marker",
                "marker-1",
                "a-u-G",
                position,
                iconpath="COT_MAPPING_2525B/a-u-G",
            )
        )

        detail = marker.find("detail")
        self.assertIsNone(detail.find("takv"))
        self.assertEqual(
            detail.find("usericon").attrib,
            {"iconsetpath": "COT_MAPPING_2525B/a-u-G"},
        )
        self.assertEqual(detail.find("contact").attrib, {"callsign": "marker"})
        self.assertEqual(detail.find("color").attrib, {"argb": "-1"})
        self.assertEqual(
            detail.find("precisionlocation").attrib,
            {"altsrc": "SRTM1"},
        )
        link = detail.find("link")
        self.assertEqual(
            {
                key: link.get(key)
                for key in ("uid", "type", "parent_callsign", "relation")
            },
            {
                "uid": client.uid,
                "type": client.cottype,
                "parent_callsign": client.callsign,
                "relation": "p-p",
            },
        )
        self.assertRegex(link.get("production_time"), self.COT_TIME_PATTERN)

    def test_pli_user_presence_fields_and_defaults(self):
        client = frogcot.ATAKClient("sender")
        position = {"lat": 1, "lon": 2, "alt": 3, "ce": 4, "le": 5}

        pli = ET.fromstring(client.pli(position))

        self.assertEqual(pli.get("version"), "2.0")
        self.assertEqual(pli.get("uid"), client.uid)
        self.assertEqual(pli.get("type"), "a-f-G-U-C")
        self.assertEqual(pli.get("how"), "m-g")
        self.assertEqual(
            pli.find("point").attrib,
            {"lat": "1", "lon": "2", "hae": "3", "ce": "4", "le": "5"},
        )
        self.assertEqual(pli.find("./detail/takv").attrib, client.takv)
        self.assertEqual(
            pli.find("./detail/contact").attrib,
            {"callsign": "sender", "endpoint": "*:-1:stcp"},
        )
        self.assertEqual(
            pli.find("./detail/uid").attrib,
            {"Droid": "sender"},
        )
        self.assertEqual(
            pli.find("./detail/precisionlocation").attrib,
            {"altsrc": "GPS", "geopointsrc": "GPS"},
        )
        self.assertEqual(
            pli.find("./detail/__group").attrib,
            {"name": "Cyan", "role": "Team Member"},
        )
        self.assertEqual(
            pli.find("./detail/status").attrib,
            {"battery": "100"},
        )
        for attribute in ("time", "start", "stale"):
            self.assertRegex(pli.get(attribute), self.COT_TIME_PATTERN)


if __name__ == "__main__":
    unittest.main()
