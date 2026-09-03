# 1. Integrate Places API via Sandbox Environment Script

Date: 2026-09-03

## Context

The restaurant recommendation agent runs as a Gemini Managed Agent (`antigravity-preview-05-2026`) inside a hosted Linux sandbox. The agent must discover candidate restaurants using Google Places API (New), verify operating schedules against future dining times, evaluate reservation policies, and generate an HTML showcase.

We evaluated three integration mechanisms:
1. Client-side Function Calling (`tools=[{"type": "function", ...}]`): requires interrupting the agent loop (`status="requires_action"`), making external network calls from the client application, and returning results over multiple round-trips.
2. Built-in Maps Grounding (`tools=[{"type": "google_maps"}]`): returns conversational text and unstructured citations, lacking structured opening hours periods and reservable flags needed for programmatic verification.
3. Sandbox Environment Script / Skill: mounting a deterministic Python helper directly into the agent's Linux container (`.agents/skills/places/`), which the agent invokes via Bash/code execution.

## Decision

We decided to integrate Google Places API (New) via a Python helper script mounted in the agent's sandbox environment.

## Consequences

- The agent can search, fetch details, compute operating hours overlap, and filter candidates autonomously in a single execution loop without client round-trips.
- The Google Maps API key must be supplied to the remote sandbox via environment variables or network allowlist credential transform.
- Deterministic calculation of operating hours is encapsulated in Python code, eliminating LLM arithmetic and scheduling errors.
