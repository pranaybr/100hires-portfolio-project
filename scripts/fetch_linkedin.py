"""Scrape recent LinkedIn profile posts for the experts in research/sources.md.

The script uses Apify's ``harvestapi/linkedin-profile-posts`` actor to fetch a
small number of recent posts for each configured LinkedIn profile. Results are
saved as individual JSON files in:

    research/linkedin-posts/

Dependency:
    python3 -m pip install apify-client

Run:
    python3 scripts/fetch_linkedin.py
"""

import json
import os
from pathlib import Path

from apify_client import ApifyClient


APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = "harvestapi/linkedin-profile-posts"
POSTS_PER_PROFILE = 5
OUTPUT_DIR = Path("research/linkedin-posts")

experts = [
    {
        "name": "chris_walker",
        "url": "https://www.linkedin.com/in/chriswalker171/",
    },
    {
        "name": "amanda_natividad",
        "url": "https://www.linkedin.com/in/amandanat/",
    },
    {
        "name": "dave_gerhardt",
        "url": "https://www.linkedin.com/in/davegerhardt/",
    },
    {
        "name": "peep_laja",
        "url": "https://www.linkedin.com/in/peeplaja/",
    },
    {
        "name": "sara_stella_lattanzio",
        "url": "https://www.linkedin.com/in/saralattanzio/",
    },
    {
        "name": "justin_welsh",
        "url": "https://www.linkedin.com/in/thejustinwelsh/",
    },
    {
        "name": "brendan_hufford",
        "url": "https://www.linkedin.com/in/brendanhufford/",
    },
    {
        "name": "diandra_escobar",
        "url": "https://www.linkedin.com/in/diandraescobar/",
    },
    {
        "name": "katelyn_bourgoin",
        "url": "https://www.linkedin.com/in/katebour/",
    },
    {
        "name": "devin_reed",
        "url": "https://www.linkedin.com/in/devinreed/",
    },
]


def build_run_input(profile_url):
    """Build the Apify actor input for one LinkedIn profile URL.

    Args:
        profile_url: A LinkedIn profile URL from ``research/sources.md``.

    Returns:
        A dictionary passed to ``Actor.call`` as ``run_input``.
    """

    return {
        "urls": [profile_url],
        "deepScrape": False,
        "postsCount": POSTS_PER_PROFILE,
    }


def save_posts(expert_name, posts):
    """Save scraped LinkedIn posts for one expert as a JSON file.

    Args:
        expert_name: Filename-safe expert identifier.
        posts: A list of dataset items returned by the Apify actor.

    Returns:
        Path to the JSON file that was written.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{expert_name}_posts.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4, ensure_ascii=False)

    return output_path


def scrape_profile_posts(client, expert):
    """Run the LinkedIn posts actor for one expert profile.

    Args:
        client: An initialized ``ApifyClient``.
        expert: A dictionary with ``name`` and ``url`` keys.

    Returns:
        A list of post records from the actor's default dataset.
    """

    run = client.actor(ACTOR_ID).call(run_input=build_run_input(expert["url"]))
    dataset_id = run["defaultDatasetId"]
    return list(client.dataset(dataset_id).iterate_items())


def main():
    """Scrape and save LinkedIn posts for every configured expert."""

    if not APIFY_API_TOKEN:
        raise RuntimeError("Set APIFY_API_TOKEN before running this script.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    client = ApifyClient(APIFY_API_TOKEN)

    for expert in experts:
        print(f"Scraping LinkedIn posts for {expert['name']}...")

        try:
            posts = scrape_profile_posts(client, expert)
            output_path = save_posts(expert["name"], posts)
            print(f"Saved {len(posts)} posts to {output_path}")
        except Exception as error:
            print(f"Skipped {expert['name']}: {error}")


if __name__ == "__main__":
    main()
