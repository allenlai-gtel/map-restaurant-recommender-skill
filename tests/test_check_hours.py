import unittest
from datetime import datetime
import sys
import os

# Ensure skill scripts directory is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".agents", "skills", "restaurant-recommender", "scripts")))

from check_hours import is_open_at, parse_place_details


class TestOperatingHoursEvaluation(unittest.TestCase):
    def setUp(self):
        # Sample weekly schedule:
        # Friday (day 5): 11:30 - 14:30, 17:30 - 23:00
        # Saturday (day 6): 18:00 - 02:00 (crosses into Sunday morning day 0)
        # Sunday (day 0): Closed
        self.sample_periods = [
            {
                "open": {"day": 5, "hour": 11, "minute": 30},
                "close": {"day": 5, "hour": 14, "minute": 30},
            },
            {
                "open": {"day": 5, "hour": 17, "minute": 30},
                "close": {"day": 5, "hour": 23, "minute": 0},
            },
            {
                "open": {"day": 6, "hour": 18, "minute": 0},
                "close": {"day": 0, "hour": 2, "minute": 0},
            },
        ]

    def test_open_during_regular_lunch_operating_period(self):
        # 2026-09-04 is a Friday
        target_dt = datetime(2026, 9, 4, 12, 30)
        is_open, message = is_open_at(self.sample_periods, target_dt)
        self.assertTrue(is_open)
        self.assertIn("11:30", message)

    def test_closed_between_operating_periods(self):
        # Friday 15:30 (between lunch and dinner)
        target_dt = datetime(2026, 9, 4, 15, 30)
        is_open, _ = is_open_at(self.sample_periods, target_dt)
        self.assertFalse(is_open)

    def test_open_during_dinner_operating_period(self):
        # Friday 19:30
        target_dt = datetime(2026, 9, 4, 19, 30)
        is_open, message = is_open_at(self.sample_periods, target_dt)
        self.assertTrue(is_open)
        self.assertIn("17:30", message)

    def test_null_regular_opening_hours_safe(self):
        raw_place = {
            "id": "places/ChIJ_null_hours",
            "displayName": {"text": "No Hours Cafe"},
            "regularOpeningHours": None
        }
        target_dt = datetime(2026, 9, 4, 19, 30)
        lean = parse_place_details(raw_place, target_dt)
        self.assertFalse(lean["is_open"])
        self.assertEqual(lean["hours_message"], "Operating hours not available")

    def test_open_crossing_midnight_pre_midnight(self):
        # Saturday 2026-09-05 at 23:00
        target_dt = datetime(2026, 9, 5, 23, 0)
        is_open, _ = is_open_at(self.sample_periods, target_dt)
        self.assertTrue(is_open)

    def test_open_crossing_midnight_post_midnight(self):
        # Sunday 2026-09-06 at 01:15 (started Saturday evening)
        target_dt = datetime(2026, 9, 6, 1, 15)
        is_open, _ = is_open_at(self.sample_periods, target_dt)
        self.assertTrue(is_open)

    def test_closed_after_overnight_closing(self):
        # Sunday 2026-09-06 at 03:00
        target_dt = datetime(2026, 9, 6, 3, 0)
        is_open, _ = is_open_at(self.sample_periods, target_dt)
        self.assertFalse(is_open)

    def test_closed_all_day_on_sunday(self):
        # Sunday 2026-09-06 at 19:30
        target_dt = datetime(2026, 9, 6, 19, 30)
        is_open, _ = is_open_at(self.sample_periods, target_dt)
        self.assertFalse(is_open)

    def test_open_24_hours(self):
        periods_247 = [{"open": {"day": 0, "hour": 0, "minute": 0}}]
        target_dt = datetime(2026, 9, 6, 19, 30)
        is_open, message = is_open_at(periods_247, target_dt)
        self.assertTrue(is_open)
        self.assertIn("24 hours", message)

    def test_parse_place_details_lean_schema(self):
        raw_place = {
            "id": "places/ChIJ12345",
            "displayName": {"text": "Trattoria Bella"},
            "formattedAddress": "123 Main St, New York, NY",
            "rating": 4.8,
            "userRatingCount": 520,
            "priceLevel": "PRICE_LEVEL_MODERATE",
            "reservable": True,
            "googleMapsUri": "https://maps.google.com/?cid=12345",
            "websiteUri": "https://trattoriabella.com",
            "editorialSummary": {"text": "Cozy rustic Italian spot known for handmade pasta."},
            "regularOpeningHours": {
                "periods": self.sample_periods
            },
            "reviews": [
                {"text": {"text": "Best cacio e pepe in the city! Must book in advance."}},
                {"text": {"text": "The tiramisu is incredible."}}
            ]
        }
        target_dt = datetime(2026, 9, 4, 19, 30)
        lean = parse_place_details(raw_place, target_dt)

        self.assertEqual(lean["place_id"], "places/ChIJ12345")
        self.assertEqual(lean["name"], "Trattoria Bella")
        self.assertTrue(lean["is_open"])
        self.assertTrue(lean["reservable"])
        self.assertEqual(lean["googleMapsUri"], "https://maps.google.com/?cid=12345")
        self.assertIn("cacio e pepe", " ".join(lean["tips"]))


if __name__ == "__main__":
    unittest.main()
