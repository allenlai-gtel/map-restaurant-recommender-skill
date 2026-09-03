---
name: restaurant-recommender
description: Discover and verify local dining spots using Google Places API and compile an HTML recommendation showcase with direct Google Maps links. Use when asked for restaurant recommendations for a specific time and location.
---

# Restaurant Recommender

End-to-end workflow to discover, verify, and present vetted restaurant recommendations using Google Places Platform tools.

## Workflow

### 1. Collect Dining Criteria

Gather any missing criteria before searching:
- **Location**: Neighborhood, city, or address.
- **Price Range**: Budget tier (e.g., $, $$, $$$, or 1-4).
- **Food Preferences & Dietary Restrictions**: Cuisine preferences, allergies, or foods to avoid.
- **Dining Window**: Target date and arrival time.

When the user specifies a date or meal period without an exact arrival time (e.g. "this Friday dinner" or "tomorrow lunch"), default dinner to `19:30` and lunch to `12:30`. State this assumed arrival time clearly in the final presentation.

### 2. Discover Candidate Pool

Search for candidate venues with a minimum rating threshold:

```bash
python .agents/skills/restaurant-recommender/scripts/search_places.py \
  --query "<cuisine/food> in <location>" \
  --min-rating 4.0 \
  --price-levels "<1,2,3,4>" \
  --limit 6
```

Completion criterion: A Candidate Pool of up to 6 structured venue objects containing `place_id`, `name`, `address`, `rating`, and `priceLevel`.

### 3. Verify Operating Hours & Reservation Profiles

Iterate through candidates and deterministically verify schedule compatibility against the user's Dining Window:

```bash
python .agents/skills/restaurant-recommender/scripts/check_hours.py \
  --place-id "<place_id>" \
  --dining-time "<YYYY-MM-DD HH:MM>"
```

Repeat until you obtain exactly **THREE Vetted Recommendations** where `is_open` is `true`.

### 4. Enrich Tips & Reservation Guidance

Extract signature dishes and reservation advice:
- Inspect `tips` and `reservable` fields from the verification output.
- If signature dish details are sparse or reservation policies require deeper verification, run a targeted web search using the agent's built-in `google_search` tool.

### 5. Build Recommendation Showcase

Assemble a clean, responsive HTML file and write it to `/workspace/restaurant_recommendations.html`.

The showcase must include:
- A header indicating the target location, cuisine, and confirmed Dining Window.
- Three distinct cards, each displaying:
  - Restaurant Name, Rating (with star icon), and Review Count.
  - Address and operating hours status for the Dining Window.
  - Reservation Profile (`Reservations Accepted` vs `Walk-ins Only / Booking Recommended`).
  - Curated signature dishes and tips.
  - A prominent call-to-action button linking directly to `googleMapsUri` (`target="_blank"`).

### 6. Deliver Recommendations

Output a concise conversational summary in the chat:
- Highlight the 3 vetted restaurants with their key appeal.
- Disclose any assumed arrival time used for verification.
- Reference the generated showcase file at `/workspace/restaurant_recommendations.html`.
