"""Fetch English YouTube transcripts and save them as text files.

This script accepts one or more YouTube video IDs from the command line, uses
the ``youtube_transcript_api`` package to fetch each video's English transcript,
and writes each transcript to an individual ``.txt`` file.

Output files are written to ``../research/youtube-transcripts/`` relative to
this script's location. In this repository, that resolves to
``research/youtube-transcripts/``.

Example:
    python scripts/fetch_youtube_transcripts.py dQw4w9WgXcQ abc123xyz

Dependency:
    pip install youtube-transcript-api
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    YouTubeTranscriptApi,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "../research/youtube-transcripts"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the transcript fetcher.

    Returns:
        An ``argparse.Namespace`` with a ``video_ids`` attribute containing the
        YouTube video IDs passed by the user.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Fetch English transcripts for one or more YouTube video IDs and "
            "save each transcript as a .txt file."
        )
    )
    parser.add_argument(
        "video_ids",
        nargs="+",
        help="One or more YouTube video IDs, not full YouTube URLs.",
    )
    return parser.parse_args()


def format_transcript(transcript_entries: Iterable[dict[str, object]]) -> str:
    """Convert transcript entries from the API into plain text.

    The YouTube Transcript API returns a list-like collection of entries, where
    each entry typically includes ``text``, ``start``, and ``duration`` fields.
    This function extracts only the spoken text and joins each caption segment
    with a newline so the output is easy to read and search.

    Args:
        transcript_entries: Transcript entries returned by
            ``YouTubeTranscriptApi().fetch``.

    Returns:
        A plain-text transcript string ending with a trailing newline.
    """

    lines = []
    for entry in transcript_entries:
        text = entry.get("text", "") if isinstance(entry, dict) else entry.text
        lines.append(str(text).strip())
    return "\n".join(line for line in lines if line) + "\n"


def transcript_path(video_id: str, output_dir: Path = OUTPUT_DIR) -> Path:
    """Build the output path for a video's transcript text file.

    Args:
        video_id: The YouTube video ID whose transcript is being saved.
        output_dir: Directory where transcript files should be written.

    Returns:
        The full path to the transcript file for ``video_id``.
    """

    return output_dir / f"{video_id}.txt"


def fetch_english_transcript(video_id: str) -> str:
    """Fetch and format the English transcript for a YouTube video.

    Args:
        video_id: The YouTube video ID to fetch.

    Returns:
        The video's English transcript as plain text.

    Raises:
        TranscriptsDisabled: If captions are disabled for the video.
        NoTranscriptFound: If captions exist, but no English transcript is
            available.
        VideoUnavailable: If the video cannot be accessed by the transcript API.
    """

    transcript_entries = YouTubeTranscriptApi().fetch(
        video_id,
        languages=["en"],
    )
    return format_transcript(transcript_entries)


def save_transcript(
    video_id: str,
    transcript_text: str,
    output_dir: Path = OUTPUT_DIR,
) -> Path:
    """Save a transcript to an individual ``.txt`` file.

    The destination directory is created automatically if it does not already
    exist.

    Args:
        video_id: The YouTube video ID used as the output filename.
        transcript_text: The formatted transcript text to write.
        output_dir: Directory where transcript files should be written.

    Returns:
        The path to the written transcript file.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = transcript_path(video_id, output_dir)
    output_path.write_text(transcript_text, encoding="utf-8")
    return output_path


def fetch_and_save_transcripts(video_ids: Iterable[str]) -> None:
    """Fetch English transcripts for a list of videos and save each to disk.

    Each video is processed independently. If a video has captions disabled, is
    unavailable, or does not have an English transcript, the script prints a
    short message and continues processing the remaining video IDs.

    Args:
        video_ids: An iterable of YouTube video IDs.
    """

    for video_id in video_ids:
        try:
            transcript_text = fetch_english_transcript(video_id)
            output_path = save_transcript(video_id, transcript_text)
            print(f"Saved transcript for {video_id}: {output_path}")
        except TranscriptsDisabled:
            print(f"Skipped {video_id}: captions are disabled.")
        except NoTranscriptFound:
            print(f"Skipped {video_id}: no English transcript was found.")
        except VideoUnavailable:
            print(f"Skipped {video_id}: video is unavailable.")


def main() -> None:
    """Run the transcript fetcher from command-line arguments."""

    args = parse_args()
    fetch_and_save_transcripts(args.video_ids)


if __name__ == "__main__":
    main()
