#!/usr/bin/env python3
"""
search_places.py - Search for restaurant candidates using Google Places API (New) Text Search.

Usage:
  python search_places.py --query "Italian restaurants in Soho New York" --min-rating 4.2 --price-levels "2,3" --limit 6
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

PRICE_MAP = {
    "1": "PRICE_LEVEL_INEXPENSIVE",
    "2": "PRICE_LEVEL_MODERATE",
    "3": "PRICE_LEVEL_EXPENSIVE",
    "4": "PRICE_LEVEL_VERY_EXPENSIVE",
    "INEXPENSIVE": "PRICE_LEVEL_INEXPENSIVE",
    "MODERATE": "PRICE_LEVEL_MODERATE",
    "EXPENSIVE": "PRICE_LEVEL_EXPENSIVE",
    "VERY_EXPENSIVE": "PRICE_LEVEL_VERY_EXPENSIVE",
}


def map_price_levels(levels_str: str | None) -> list[str] | None:
    if not levels_str:
        return None
    mapped = []
    for token in levels_str.split(","):
        token = token.strip().upper()
        if token in PRICE_MAP:
            mapped.append(PRICE_MAP[token])
    return mapped if mapped else None


def parse_search_results(raw_response: dict, min_rating: float = 4.0, limit: int = 6) -> list[dict]:
    """
    Parses raw Places API text search response into a lean candidate pool.
    """
    places = raw_response.get("places", [])
    candidates = []

    for place in places:
        rating = place.get("rating", 0.0)
        if rating < min_rating:
            continue

        place_id = place.get("id", "")
        name = place.get("displayName", {}).get("text", "")
        address = place.get("formattedAddress", "")
        review_count = place.get("userRatingCount", 0)
        price_level = place.get("priceLevel", "PRICE_LEVEL_UNSPECIFIED")
        summary = place.get("editorialSummary", {}).get("text", "")

        candidates.append({
            "place_id": place_id,
            "name": name,
            "address": address,
            "rating": rating,
            "userRatingCount": review_count,
            "priceLevel": price_level,
            "summary": summary
        })

        if len(candidates) >= limit:
            break

    return candidates


def search_places(query: str, min_rating: float = 4.0, price_levels: list[str] | None = None, limit: int = 6, api_key: str | None = None) -> list[dict]:
    """
    Sends request to Google Places API (New) Text Search endpoint.
    """
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,"
            "places.rating,places.userRatingCount,places.priceLevel,places.editorialSummary"
        )
    }
    if api_key:
        headers["X-Goog-Api-Key"] = api_key

    body = {
        "textQuery": query,
        "pageSize": min(20, max(limit * 2, 10))
    }

    if min_rating and min_rating > 0.0:
        body["minRating"] = min_rating

    if price_levels:
        body["priceLevels"] = price_levels

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            return parse_search_results(raw, min_rating=min_rating, limit=limit)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        if e.code in (401, 403):
            raise RuntimeError(
                f"Places text search failed ({e.code}): Unauthorized. "
                f"Ensure the sandbox credential proxy is active or supply GOOGLE_MAPS_API_KEY. Details: {err_body}"
            )
        raise RuntimeError(f"Places text search failed ({e.code}): {err_body}")


def main():
    parser = argparse.ArgumentParser(description="Search candidate restaurants using Google Places API (New).")
    parser.add_argument("--query", required=True, help="Text search query (e.g. 'ramen in Central Tokyo')")
    parser.add_argument("--min-rating", type=float, default=4.0, help="Minimum rating threshold (default: 4.0)")
    parser.add_argument("--price-levels", help="Comma-separated price levels: 1, 2, 3, 4 or MODERATE, EXPENSIVE")
    parser.add_argument("--limit", type=int, default=6, help="Candidate pool size (default: 6)")
    parser.add_argument("--api-key", default=os.getenv("GOOGLE_MAPS_API_KEY"), help="Google Maps API Key (optional if proxy credential injection is enabled)")

    args = parser.parse_args()

    mapped_prices = map_price_levels(args.price_levels)

    try:
        results = search_places(
            query=args.query,
            min_rating=args.min_rating,
            price_levels=mapped_prices,
            limit=args.limit,
            api_key=args.api_key
        )
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
