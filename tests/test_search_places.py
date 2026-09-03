import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".agents", "skills", "restaurant-recommender", "scripts")))

from search_places import parse_search_results, map_price_levels


class TestPlaceSearch(unittest.TestCase):
    def test_map_price_levels(self):
        self.assertEqual(map_price_levels("1"), ["PRICE_LEVEL_INEXPENSIVE"])
        self.assertEqual(map_price_levels("2,3"), ["PRICE_LEVEL_MODERATE", "PRICE_LEVEL_EXPENSIVE"])
        self.assertEqual(map_price_levels("MODERATE,VERY_EXPENSIVE"), ["PRICE_LEVEL_MODERATE", "PRICE_LEVEL_VERY_EXPENSIVE"])
        self.assertIsNone(map_price_levels(None))
        self.assertIsNone(map_price_levels(""))

    def test_parse_search_results_lean_and_filtered(self):
        raw_api_data = {
            "places": [
                {
                    "id": "places/place_1",
                    "displayName": {"text": "Top Bistro"},
                    "formattedAddress": "100 Spring St, New York, NY",
                    "rating": 4.7,
                    "userRatingCount": 350,
                    "priceLevel": "PRICE_LEVEL_MODERATE",
                    "editorialSummary": {"text": "French-inspired contemporary bistro."}
                },
                {
                    "id": "places/place_2",
                    "displayName": {"text": "Low Rated Diner"},
                    "formattedAddress": "102 Spring St, New York, NY",
                    "rating": 3.8,
                    "userRatingCount": 80,
                    "priceLevel": "PRICE_LEVEL_INEXPENSIVE"
                },
                {
                    "id": "places/place_3",
                    "displayName": {"text": "Superb Trattoria"},
                    "formattedAddress": "104 Spring St, New York, NY",
                    "rating": 4.9,
                    "userRatingCount": 1200,
                    "priceLevel": "PRICE_LEVEL_EXPENSIVE",
                    "editorialSummary": {"text": "Handmade pasta and wood-fired pizza."}
                }
            ]
        }

        # Filter min_rating 4.0, limit 2
        results = parse_search_results(raw_api_data, min_rating=4.0, limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "Top Bistro")
        self.assertEqual(results[0]["rating"], 4.7)
        self.assertEqual(results[1]["name"], "Superb Trattoria")
        # Ensure place_2 with rating 3.8 was excluded
        self.assertNotIn("Low Rated Diner", [r["name"] for r in results])


if __name__ == "__main__":
    unittest.main()
