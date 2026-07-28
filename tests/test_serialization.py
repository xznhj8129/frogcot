import re
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

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

    def test_marker_uses_requested_stale_time(self):
        client = frogcot.ATAKClient("sender")
        position = {
            "lat": 36.530440,
            "lon": -83.216383,
            "alt": 3,
            "ce": 4,
            "le": 5,
        }

        with patch(
            "frogcot.frogcot.generate_cot_time",
            return_value="timestamp",
        ) as generate_time:
            client.cot_marker(
                "marker",
                "marker-1",
                "a-f-G",
                position,
                staletime=120,
            )

        generate_time.assert_any_call(120)

    def test_xml_to_cot_accepts_decimal_version(self):
        event = frogcot.xml_to_cot(
            '<event version="2.0" type="a-f-G" how="m-g">'
            '<point lat="36.530440" lon="-83.216383" hae="3" ce="4" le="5"/>'
            '</event>'
        )

        self.assertEqual(event.version, 2)

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
