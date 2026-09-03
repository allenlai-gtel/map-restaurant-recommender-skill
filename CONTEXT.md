# Restaurant Recommendation Agent

Domain model and ubiquitous language for the autonomous restaurant recommendation agent using Gemini Managed Agent and Google Maps Platform.

## Language

**Candidate Restaurant**:
A potential dining venue discovered during initial search matching location, cuisine, or price criteria, prior to detailed availability verification.
_Avoid_: Lead, option, prospect

**Candidate Pool**:
A pre-fetched batch of candidate restaurants (typically 6–10) retrieved in a single search to provide immediate alternates if primary candidates fail schedule checks.
_Avoid_: Search results, shortlist

**Vetted Recommendation**:
A finalized restaurant selection that has passed all verification checks, specifically operating schedule compatibility, high customer rating, and reservation status.
_Avoid_: Pick, choice, suggestion

**Dining Window**:
The target date, day of week, and time interval when the user intends to dine.
_Avoid_: Reservation slot, booking time, visit time

**Operating Period**:
A defined day-of-week and time-range span during which a venue is actively open for dining service according to its published regular schedule.
_Avoid_: Business hours, open hours, shift

**Reservation Profile**:
The structured assessment of whether a restaurant accepts reservations, requires walk-ins, or strongly recommends booking in advance.
_Avoid_: Booking policy, table status

**Recommendation Showcase**:
The standalone HTML presentation file generated in the workspace containing formatted venue details, signature dish highlights, and direct Google Maps navigation links.
_Avoid_: Report, export, dashboard, webpage
