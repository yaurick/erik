"""Journey-logic tests for the OLCI-open push template."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from fifteen_below import notification_body, render, render_json, strip_journey_wrapper, unmerged_markers

ROOT = Path(__file__).resolve().parents[1]
PAYLOADS = ROOT / "payloads"
FIXTURES = ROOT / "fixtures"


def _load(path: Path) -> str | dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json" and not text.lstrip().startswith("<"):
        return json.loads(text)
    return text


def _booking(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _template(name: str) -> str:
    return (PAYLOADS / name).read_text(encoding="utf-8")


ORIGINAL = _template("original.json")
CORRECTED = _template("corrected.json")


class OlciJourneyLogicTests(unittest.TestCase):
    def test_direct_flight_renders_flight_number_and_city_pair(self):
        payload = render_json(CORRECTED, _booking("direct_ala_nqz.json"))
        body = notification_body(payload)
        self.assertIn("KC854", body)
        self.assertIn("Almaty, Kazakhstan - Astana, Kazakhstan", body)
        self.assertIn("surname=KASSYM", body)
        self.assertIn("pnrNumber=ABC123", body)
        self.assertTrue(body.startswith("Check in online for your KC854 "))
        json.dumps(payload)  # stays serialisable

    def test_connecting_journey_uses_true_od_not_first_segment(self):
        body = notification_body(render_json(CORRECTED, _booking("connecting_ala_ist_lhr.json")))
        self.assertIn("KC923", body)
        self.assertNotIn("KC501", body)
        self.assertIn("Almaty, Kazakhstan - London, United Kingdom", body)
        self.assertNotIn("Almaty, Kazakhstan - Istanbul", body)

    def test_return_trip_only_shows_the_journey_that_opened_check_in(self):
        original = notification_body(render_json(ORIGINAL, _booking("return_trip.json")))
        corrected = notification_body(render_json(CORRECTED, _booking("return_trip.json")))

        self.assertIn("Almaty, Kazakhstan-Astana, Kazakhstan", original)
        self.assertIn("Astana, Kazakhstan-Almaty, Kazakhstan", original)

        self.assertIn("Almaty, Kazakhstan - Astana, Kazakhstan", corrected)
        self.assertNotIn("Astana, Kazakhstan - Almaty, Kazakhstan", corrected)

    def test_cancelled_relevant_flight_is_omitted(self):
        body = notification_body(render_json(CORRECTED, _booking("cancelled_relevant.json")))
        self.assertNotIn("KC210", body)
        self.assertNotIn("Almaty, Kazakhstan - Dubai", body)
        self.assertIn("Check in online for your", body)

    def test_original_deep_link_is_not_substituted(self):
        body = notification_body(render_json(ORIGINAL, _booking("direct_ala_nqz.json")))
        self.assertIn("surname=%7B%7BPAX_LASTNAME%7D%7D", body)
        self.assertIn("pnrNumber=%7B%7BPNR%7D%7D", body)
        self.assertNotIn("surname=KASSYM", body)

    def test_corrected_deep_link_encodes_special_characters(self):
        body = notification_body(render_json(CORRECTED, _booking("two_relevant_flights.json")))
        self.assertIn("surname=O%27BRIEN", body)
        self.assertIn("pnrNumber=MLT222", body)
        self.assertIn("#/6", body)

    def test_two_relevant_flights_are_space_separated_and_city_pair_is_once(self):
        body = notification_body(render_json(CORRECTED, _booking("two_relevant_flights.json")))
        self.assertIn("KC923 KC501", body)
        self.assertEqual(body.count("Almaty, Kazakhstan - London, United Kingdom"), 1)

    def test_fcm_and_apns_bodies_match(self):
        payload = render_json(CORRECTED, _booking("direct_ala_nqz.json"))
        self.assertEqual(
            payload["notification"]["body"],
            payload["apns"]["payload"]["aps"]["alert"]["body"],
        )
        self.assertEqual(
            payload["notification"]["title"],
            payload["apns"]["payload"]["aps"]["alert"]["title"],
        )
        self.assertEqual(payload["android"]["priority"], "high")
        self.assertEqual(payload["apns"]["payload"]["aps"]["sound"], "default")
        self.assertEqual(payload["apns"]["payload"]["aps"]["mutable-content"], 1)
        self.assertEqual(payload["apns"]["payload"]["aps"]["content-available"], 1)

    def test_original_template_is_not_json_until_merged(self):
        raw = (PAYLOADS / "original.json").read_text(encoding="utf-8")
        self.assertIn("<ENABLE_JOURNEY_LOGIC>", raw)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(raw)

    def test_corrected_template_is_valid_json_before_merge(self):
        raw, enabled = strip_journey_wrapper(
            (PAYLOADS / "corrected.json").read_text(encoding="utf-8")
        )
        self.assertTrue(enabled)
        template = json.loads(raw)
        self.assertIn("[for-each flight]", template["notification"]["body"])
        self.assertIn("<PNR>", template["data"]["pnr"])
        self.assertIsInstance(template["data"]["pnr"], str)

    def test_literal_encode_leaves_dynamic_tags_as_static_copy(self):
        body = notification_body(
            render_json(ORIGINAL, _booking("direct_ala_nqz.json"), literal_encode=True)
        )
        self.assertIn("[for-each flight]", body)
        self.assertIn("<CARRIER_CODE>", body)
        self.assertIn("%7B%7BPAX_LASTNAME%7D%7D", body)
        self.assertNotIn("KC854", body)

    def test_corrected_render_has_no_leftover_template_markers(self):
        payload = render_json(CORRECTED, _booking("two_relevant_flights.json"))
        blob = json.dumps(payload)
        self.assertEqual(unmerged_markers(blob), [])
        self.assertEqual(unmerged_markers(payload["notification"]["body"]), [])
        self.assertEqual(unmerged_markers(payload["data"]["body"]), [])
        self.assertEqual(unmerged_markers(payload["data"]["deepLink"]), [])
        self.assertEqual(payload["data"]["pnr"], "MLT222")
        self.assertEqual(payload["data"]["surname"], "O'BRIEN")
        self.assertEqual(payload["apns"]["payload"]["pnr"], "MLT222")
        for value in payload["data"].values():
            self.assertIsInstance(value, str)

    def test_data_and_notification_bodies_match(self):
        payload = render_json(CORRECTED, _booking("direct_ala_nqz.json"))
        self.assertEqual(payload["notification"]["body"], payload["data"]["body"])
        self.assertEqual(payload["data"]["flightNumbers"].strip(), "KC854")
        self.assertEqual(payload["data"]["journey"], "Almaty, Kazakhstan - Astana, Kazakhstan")
        self.assertTrue(payload["data"]["deepLink"].endswith("surname=KASSYM&pnrNumber=ABC123#/6"))

    def test_render_produces_valid_json_with_encoded_newline(self):
        rendered = render(CORRECTED, _booking("direct_ala_nqz.json"))
        payload = json.loads(rendered)
        self.assertIn("\n", payload["notification"]["body"])
        self.assertIn("Open your booking:", payload["notification"]["body"])


if __name__ == "__main__":
    unittest.main()
