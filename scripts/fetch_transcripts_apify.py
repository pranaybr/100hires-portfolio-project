"""Fetch YouTube transcripts through Apify and save them as text files.

Edit ``creator_name`` and ``video_urls`` below each time you want to fetch a
specific set of videos. The script calls an Apify YouTube transcript scraper
actor and saves one cleaned text file per video in:

    research/youtube-transcripts/

Dependency:
    python3 -m pip install apify-client

Run:
    python3 scripts/fetch_transcripts_apify.py
"""

import json
import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from apify_client import ApifyClient



creator_name = "chris_walker"
video_urls = [
    "https://www.youtube.com/watch?v=jjLryGdFJZA",
    "https://www.youtube.com/watch?v=dZx610FbOBc",
    "https://www.youtube.com/watch?v=YdEpv0ZAP10",
    "https://www.youtube.com/watch?v=JkXom1dC_20",
    "https://www.youtube.com/watch?v=WVD9dzd0SL4",
]

OUTPUT_DIR = Path("research/youtube-transcripts")


def get_video_id(video_url):
    """Extract a YouTube video ID from common YouTube URL formats.

    Args:
        video_url: A full YouTube URL, such as a watch URL, shorts URL, or
            youtu.be URL.

    Returns:
        The parsed video ID, or a filename-safe fallback if no ID is found.
    """

    parsed_url = urlparse(video_url)

    if parsed_url.hostname in {"youtu.be", "www.youtu.be"}:
        return parsed_url.path.strip("/")

    if parsed_url.path.startswith("/shorts/"):
        return parsed_url.path.split("/")[2]

    query_params = parse_qs(parsed_url.query)
    if "v" in query_params:
        return query_params["v"][0]

    return re.sub(r"[^A-Za-z0-9_-]+", "_", video_url).strip("_")


def normalize_transcript_value(value):
    """Convert a transcript value from Apify into readable text.

    Args:
        value: Transcript data from an Apify dataset item. It may be a string,
            a list of text segments, or a dictionary-like object.

    Returns:
        A plain text representation of the transcript.
    """

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        lines = []
        for segment in value:
            if isinstance(segment, str):
                lines.append(segment)
            elif isinstance(segment, dict):
                lines.append(str(segment.get("text", "")))
        return "\n".join(line.strip() for line in lines if line.strip())

    if isinstance(value, dict):
        return json.dumps(value, indent=2)

    return str(value or "")


def extract_transcript_text(dataset_item):
    """Find transcript text in a dataset item returned by the Apify actor.

    Args:
        dataset_item: One item from the actor's default dataset.

    Returns:
        Transcript text if present, otherwise an empty string.
    """

    possible_fields = [
        "transcript",
        "transcripts",
        "text",
        "captions",
        "subtitles",
    ]

    for field in possible_fields:
        if field in dataset_item:
            return normalize_transcript_value(dataset_item[field]).strip()

    return ""


def save_transcript(video_url, transcript_text):
    """Save transcript text for one video URL.

    Args:
        video_url: The YouTube URL being processed.
        transcript_text: Clean transcript text to save.

    Returns:
        The output path that was written.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    video_id = get_video_id(video_url)
    output_path = OUTPUT_DIR / f"{creator_name}_{video_id}.txt"
    output_path.write_text(transcript_text + "\n", encoding="utf-8")
    return output_path


def fetch_transcript(client, video_url):
    """Run the Apify actor for one YouTube URL and return transcript text.

    Args:
        client: An initialized ``ApifyClient``.
        video_url: The YouTube URL to fetch.

    Returns:
        Transcript text returned by the actor.

    Raises:
        ValueError: If the actor run finishes but no transcript is found.
    """

    run = client.actor(ACTOR_ID).call(
        run_input={"startUrls": [{"url": video_url}]}
    )

    dataset_id = run["defaultDatasetId"]
    for item in client.dataset(dataset_id).iterate_items():
        transcript_text = extract_transcript_text(item)
        if transcript_text:
            return transcript_text

    raise ValueError("No transcript text found in Apify dataset")


def main():
    """Fetch and save transcripts for all configured video URLs."""

    if not APIFY_API_TOKEN:
        raise RuntimeError("Set APIFY_API_TOKEN before running this script.")

    client = ApifyClient(APIFY_API_TOKEN)

    for video_url in video_urls:
        print(f"Fetching transcript with Apify: {video_url}")

        try:
            transcript_text = fetch_transcript(client, video_url)
            output_path = save_transcript(video_url, transcript_text)
            print(f"Saved: {output_path}")
        except Exception as error:
            print(f"Skipped {video_url}: {error}")


if __name__ == "__main__":
    main()
