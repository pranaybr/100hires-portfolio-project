"""Download and clean auto-generated English YouTube transcripts with yt-dlp.

Requirements:
    - Python standard library only.
    - The ``yt-dlp`` command-line tool must be installed and available on PATH.

Usage:
    1. Set ``creator_name`` and ``video_urls`` below.
    2. Run: ``python scripts/fetch_youtube_transcripts.py``

The script downloads auto-generated English subtitles as ``.en.vtt`` files,
removes timestamps and VTT/HTML tags with regular expressions, then writes clean
plain-text transcripts to ``research/youtube-transcripts/``. It uses the
``cookies.txt`` file in the project root for YouTube session authentication.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


creator_name = "chris_walker"
video_urls = [
    "https://www.youtube.com/watch?v=jjLryGdFJZA",
    "https://www.youtube.com/watch?v=dZx610FbOBc",
    "https://www.youtube.com/watch?v=YdEpv0ZAP10",
    "https://www.youtube.com/watch?v=JkXom1dC_20",
    "https://www.youtube.com/watch?v=WVD9dzd0SL4",
]

OUTPUT_DIR = Path("research/youtube-transcripts")
COOKIES_FILE = Path("cookies.txt")
YT_DLP_COMMAND = [sys.executable, "-m", "yt_dlp"]
YT_DLP_EXTRACTOR_ARGS = ["--extractor-args", "youtube:player_client=android"]
YT_DLP_IMPERSONATION = ["--impersonate", "chrome"]


def clean_vtt_text(vtt_text):
    """Convert raw VTT subtitle text into a clean plain-text transcript.

    Args:
        vtt_text: The raw contents of a ``.vtt`` subtitle file downloaded by
            ``yt-dlp``.

    Returns:
        A cleaned transcript string with VTT headers, timestamps, cue settings,
        and inline tags removed.
    """

    cleaned_lines = []

    for line in vtt_text.splitlines():
        line = line.strip()

        if not line:
            continue
        if line == "WEBVTT":
            continue
        if line.startswith(("Kind:", "Language:")):
            continue
        if "-->" in line:
            continue

        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"&amp;", "&", line)
        line = re.sub(r"&lt;", "<", line)
        line = re.sub(r"&gt;", ">", line)
        line = re.sub(r"\s+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines) + "\n"


def get_video_id(video_url):
    """Ask yt-dlp for the canonical video ID for a YouTube URL.

    Args:
        video_url: A full YouTube video URL.

    Returns:
        The canonical YouTube video ID reported by ``yt-dlp``.

    Raises:
        subprocess.CalledProcessError: If ``yt-dlp`` cannot read the metadata.
        KeyError: If the metadata response does not contain an ``id`` field.
    """

    command = [
        *YT_DLP_COMMAND,
        "--skip-download",
        "--dump-json",
        *YT_DLP_EXTRACTOR_ARGS,
        *YT_DLP_IMPERSONATION,
        "--cookies",
        str(COOKIES_FILE),
        video_url,
    ]

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    video_info = json.loads(result.stdout)

    return video_info["id"]


def download_auto_english_vtt(video_url, video_id, download_dir):
    """Download a video's auto-generated English subtitles as a VTT file.

    Args:
        video_url: The full YouTube URL to process.
        video_id: The canonical YouTube video ID.
        download_dir: Temporary directory where ``yt-dlp`` should save the VTT.

    Returns:
        The path to the downloaded ``.en.vtt`` file.

    Raises:
        subprocess.CalledProcessError: If ``yt-dlp`` fails for the video.
        FileNotFoundError: If ``yt-dlp`` completes but no English VTT is found.
    """

    output_template = str(download_dir / "%(id)s.%(ext)s")
    subprocess.run(
        [
            *YT_DLP_COMMAND,
            "--skip-download",
            *YT_DLP_EXTRACTOR_ARGS,
            *YT_DLP_IMPERSONATION,
            "--write-auto-subs",
            "--sub-lang",
            "en",
            "--sub-format",
            "vtt",
            "--sleep-subtitles",
            "5",
            "--cookies",
            str(COOKIES_FILE),
            "--output",
            output_template,
            video_url,
        ],
        check=True,
    )

    matches = sorted(download_dir.glob(f"{video_id}.en*.vtt"))
    if not matches:
        raise FileNotFoundError(f"No English VTT file found for {video_id}")

    return matches[0]


def save_clean_transcript(video_id, vtt_path):
    """Clean a downloaded VTT file and save it as a transcript text file.

    Args:
        video_id: The YouTube video ID being processed.
        vtt_path: Path to the downloaded ``.en.vtt`` file.

    Returns:
        The path to the saved plain-text transcript.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_vtt = vtt_path.read_text(encoding="utf-8")
    cleaned_text = clean_vtt_text(raw_vtt)

    output_path = OUTPUT_DIR / f"{creator_name}_{video_id}.txt"
    output_path.write_text(cleaned_text, encoding="utf-8")

    return output_path


def main():
    """Download, clean, and save transcripts for all configured video URLs."""

    for video_url in video_urls:
        print(f"Downloading transcript for {video_url}...")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                video_id = get_video_id(video_url)
                vtt_path = download_auto_english_vtt(video_url, video_id, Path(temp_dir))
                output_path = save_clean_transcript(video_id, vtt_path)
                print(f"Saved: {output_path}")
        except Exception as error:
            print(f"Skipped {video_url}: {error}")


if __name__ == "__main__":
    main()
