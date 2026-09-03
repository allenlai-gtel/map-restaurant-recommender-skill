#!/usr/bin/env python3
"""
check_hours.py - Inspect Google Place Details and deterministically verify operating hours.

Usage:
  python check_hours.py --place-id "places/ChIJ..." --dining-time "2026-09-04 19:30"
"""

import argparse
import datetime
import json
import os
import sys
import urllib.request
import urllib.error

MINUTES_IN_WEEK = 7 * 24 * 60  # 10,080 minutes


def is_open_at(periods: list[dict], target_dt: datetime.datetime) -> tuple[bool, str]:
    """
    Deterministically evaluates whether target_dt falls within any operating period.
    Google Places API periods use:
      day: 0 (Sunday) to 6 (Saturday)
      hour: 0 to 23
      minute: 0 to 59
    """
    if not periods:
        return False, "Operating hours not available"

    # Single period with no close time indicates 24 hours open
    if len(periods) == 1 and "close" not in periods[0]:
        return True, "Open 24 hours"

    # Convert target_dt to Google day (Sunday=0, Monday=1, ..., Saturday=6)
    target_google_day = (target_dt.weekday() + 1) % 7
    target_minute_of_week = target_google_day * 24 * 60 + target_dt.hour * 60 + target_dt.minute

    matching_period_str = ""

    for period in periods:
        open_info = period.get("open")
        close_info = period.get("close")

        if not open_info:
            continue

        if not close_info:
            # Open 24h from this open point
            return True, "Open 24 hours"

        open_day = open_info.get("day", 0)
        open_hr = open_info.get("hour", 0)
        open_min = open_info.get("minute", 0)

        close_day = close_info.get("day", 0)
        close_hr = close_info.get("hour", 0)
        close_min = close_info.get("minute", 0)

        open_total = open_day * 24 * 60 + open_hr * 60 + open_min
        close_total = close_day * 24 * 60 + close_hr * 60 + close_min

        # Calculate duration of this operating period
        span = (close_total - open_total) % MINUTES_IN_WEEK
        if span == 0:
            span = MINUTES_IN_WEEK

        # Calculate offset of target from open time
        offset = (target_minute_of_week - open_total) % MINUTES_IN_WEEK

        if offset < span:
            time_str = f"{open_hr:02d}:{open_min:02d} - {close_hr:02d}:{close_min:02d}"
            return True, f"Open ({time_str})"

    return False, "Closed at requested dining time"


def parse_place_details(raw_place: dict, target_dt: datetime.datetime) -> dict:
    """
    Extracts lean verified fields from raw Places API response.
    """
    place_id = raw_place.get("id", "")
    display_name = (raw_place.get("displayName") or {}).get("text", "")
    address = raw_place.get("formattedAddress", "")
    rating = raw_place.get("rating", 0.0)
    review_count = raw_place.get("userRatingCount", 0)
    price_level = raw_place.get("priceLevel", "PRICE_LEVEL_UNSPECIFIED")
    reservable = raw_place.get("reservable", False)
    google_maps_uri = raw_place.get("googleMapsUri", "")
    website_uri = raw_place.get("websiteUri", "")
    editorial_summary = (raw_place.get("editorialSummary") or {}).get("text", "")

    opening_hours_obj = raw_place.get("regularOpeningHours") or {}
    periods = opening_hours_obj.get("periods") or []
    is_open, hours_message = is_open_at(periods, target_dt)

    # Extract signature tips from editorial summary and reviews
    tips = []
    if editorial_summary:
        tips.append(editorial_summary)

    for review in raw_place.get("reviews", []):
        review_text = review.get("text", {}).get("text", "").strip()
        if review_text and len(tips) < 3:
            # Truncate long reviews to concise tip snippets
            snippet = review_text[:160] + "..." if len(review_text) > 160 else review_text
            tips.append(snippet)

    return {
        "place_id": place_id,
        "name": display_name,
        "address": address,
        "rating": rating,
        "userRatingCount": review_count,
        "priceLevel": price_level,
        "reservable": reservable,
        "is_open": is_open,
        "hours_message": hours_message,
        "googleMapsUri": google_maps_uri,
        "websiteUri": website_uri,
        "tips": tips
    }


def fetch_place_details(place_id: str, api_key: str) -> dict:
    """
    Fetches place details from Google Places API (New).
    """
    if not place_id.startswith("places/"):
        formatted_id = f"places/{place_id}"
    else:
        formatted_id = place_id

    url = f"https://places.googleapis.com/v1/{formatted_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "id,displayName,formattedAddress,rating,userRatingCount,priceLevel,"
            "regularOpeningHours,reservable,websiteUri,googleMapsUri,editorialSummary,reviews"
        )
    }

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"Places API request failed ({e.code}): {body}")


def main():
    parser = argparse.ArgumentParser(description="Inspect Place Details and verify operating hours.")
    parser.add_argument("--place-id", required=True, help="Google Place ID (e.g., places/ChIJ...)")
    parser.add_argument("--dining-time", required=True, help="Target dining datetime, formatted 'YYYY-MM-DD HH:MM'")
    parser.add_argument("--api-key", default=os.getenv("GOOGLE_MAPS_API_KEY"), help="Google Maps API Key")

    args = parser.parse_args()

    if not args.api_key:
        print(json.dumps({"error": "GOOGLE_MAPS_API_KEY environment variable or --api-key required."}), file=sys.stderr)
        sys.exit(1)

    try:
        target_dt = datetime.datetime.strptime(args.dining_time, "%Y-%m-%d %H:%M")
    except ValueError:
        print(json.dumps({"error": f"Invalid dining-time format '{args.dining_time}'. Expected 'YYYY-MM-DD HH:MM'"}), file=sys.stderr)
        sys.exit(1)

    try:
        raw_place = fetch_place_details(args.place_id, args.api_key)
        vetted_data = parse_place_details(raw_place, target_dt)
        print(json.dumps(vetted_data, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
