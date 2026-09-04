#!/usr/bin/env python3
# ==============================================================================
# NOTICE: FOR HUMAN DEVELOPER LOCAL TESTING ONLY.
# DO NOT RUN THIS SCRIPT FROM THE MANAGED AGENT OR INSIDE THE SANDBOX.
# The agent should only invoke skills/scripts under .agents/skills/.
# ==============================================================================
"""
local_dev_runner.py - Developer test script to launch the Restaurant Recommendation
Managed Agent from a local development workstation using the Gemini Interactions API
and google-genai SDK.
"""

import os
import sys

try:
    from google import genai
except ImportError:
    print("google-genai SDK not installed. Install with: pip install google-genai", file=sys.stderr)


def run_demo():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not gemini_api_key:
        print("Please set GEMINI_API_KEY environment variable.", file=sys.stderr)
        return

    if not maps_api_key:
        print("Notice: GOOGLE_MAPS_API_KEY not set locally. In a sandbox environment with egress proxy credential injection, Places API calls authenticate automatically.", file=sys.stderr)

    client = genai.Client()

    # Load local AGENTS.md and skill files to pass inline into the remote sandbox environment
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agents_md_path = os.path.join(base_dir, ".agents", "AGENTS.md")
    skill_md_path = os.path.join(base_dir, ".agents", "skills", "restaurant-recommender", "SKILL.md")
    search_py_path = os.path.join(base_dir, ".agents", "skills", "restaurant-recommender", "scripts", "search_places.py")
    check_py_path = os.path.join(base_dir, ".agents", "skills", "restaurant-recommender", "scripts", "check_hours.py")

    with open(agents_md_path, "r", encoding="utf-8") as f:
        agents_md_content = f.read()
    with open(skill_md_path, "r", encoding="utf-8") as f:
        skill_md_content = f.read()
    with open(search_py_path, "r", encoding="utf-8") as f:
        search_py_content = f.read()
    with open(check_py_path, "r", encoding="utf-8") as f:
        check_py_content = f.read()

    print("Launching Gemini Managed Agent interaction...")

    env_vars = {}
    if maps_api_key:
        env_vars["GOOGLE_MAPS_API_KEY"] = maps_api_key

    interaction = client.interactions.create(
        agent="antigravity-preview-05-2026",
        input="I'm looking for 3 great Japanese restaurants in Banqiao, Taipei for this Friday dinner. Price range $ to $$.",
        environment={
            "type": "remote",
            "variables": env_vars,
            "sources": [
                {
                    "type": "inline",
                    "target": ".agents/AGENTS.md",
                    "content": agents_md_content
                },
                {
                    "type": "inline",
                    "target": ".agents/skills/restaurant-recommender/SKILL.md",
                    "content": skill_md_content
                },
                {
                    "type": "inline",
                    "target": ".agents/skills/restaurant-recommender/scripts/search_places.py",
                    "content": search_py_content
                },
                {
                    "type": "inline",
                    "target": ".agents/skills/restaurant-recommender/scripts/check_hours.py",
                    "content": check_py_content
                }
            ]
        }
    )

    print("\n=== Agent Response ===")
    print(interaction.output_text)
    print("\nEnvironment ID:", getattr(interaction, "environment_id", "N/A"))


if __name__ == "__main__":
    run_demo()
