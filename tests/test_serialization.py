import unittest
import xml.etree.ElementTree as ET

import frogcot


class SerializationTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
