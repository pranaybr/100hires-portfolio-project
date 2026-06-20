# Research Collection Log

## YouTube Transcripts

Attempted to collect Chris Walker YouTube transcripts with `yt-dlp` using
`cookies.txt`. The default YouTube client could not see requested English
captions because YouTube required PO-token/SABR handling. Switching `yt-dlp` to
the Android player client exposed the English auto-caption tracks, but subtitle
file downloads returned `HTTP Error 429: Too Many Requests`.

The current fallback path is `scripts/fetch_transcripts_apify.py`, which uses an
Apify YouTube transcript actor and saves cleaned transcript text into
`research/youtube-transcripts/`.

## LinkedIn Posts

Replaced mock LinkedIn post generation with `scripts/fetch_linkedin.py`, which
uses Apify actor `harvestapi/linkedin-profile-posts` for the ten LinkedIn
profiles listed in `research/sources.md`.

The script writes one JSON file per expert into `research/linkedin-posts/`.
Set `APIFY_API_TOKEN` before running either Apify script.
