# ZEX — ZTV Extractor

**Language :** [🇬🇧 English](#english)

---

ZEX (ZTV Extractor) is a Python script for inspecting movie pages on Cinema Zetware, detecting the `vsembed` video player, and identifying HLS manifests (`master.m3u8`) along with the available stream resolutions.

## Features

- Opens movie pages using Chromium through Playwright.
- Extracts the movie title from the HTML `h1` element.
- Identifies the TMDB ID from the page URL.
- Locates the `vsembed` player iframe and nested iframes.
- Detects `master.m3u8` URLs from network responses.
- Checks video playback status.
- Parses HLS manifests to identify available resolutions and stream URLs.
- Displays results in a formatted terminal output.

## Requirements

- Python 3.9 or later.
- Playwright for Python.
- A Chromium browser supported by Playwright.
- An internet connection.
- Authorized access to the page and stream being inspected.

## Installation

### 1. Set up the project

Save the script as `extract.py`.

```text
ZEx/
├── extract.py
├── requirements.txt
├── README.md
└── .gitignore
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

If the `python` command is unavailable, use `python3`.

Contents of `requirements.txt`:

```text
playwright
```

## Usage

Run the script with the movie page URL as an argument:

```bash
python extract.py "https://cinema.zetware.id/watch/tmdb-mov-24428"
```

This URL is an example of a movie page to inspect. You can replace it with another accessible URL that you are authorized to examine.

### Parameters and components

| Parameter / Component | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `url`                 | The movie page URL supplied when running the script  |
| `page.goto(url)`      | Opens the page using the supplied URL                |
| `vsembed`             | The player iframe pattern searched for by the script |
| `master.m3u8`         | The HLS manifest inspected for stream variants       |

## Workflow

1. Opens the movie page in Chromium.
2. Extracts the title and identifies the TMDB ID.
3. Monitors network responses for `master.m3u8`.
4. Locates the `vsembed` iframe and nested player iframes.
5. Attempts to activate the player and checks playback status.
6. Parses the HLS manifest to identify resolutions advertised by the server.
7. Prints the results in the terminal.

## Example Output

```text
═════════════════════════════════════════════════════════════════
                 🎬 VIDEO STREAM EXTRACTION RESULTS 🎬
═════════════════════════════════════════════════════════════════
 📌 Movie Title : Example Movie Title
 🆔 TMDB ID     : 24428
─────────────────────────────────────────────────────────────────
 📐 AVAILABLE RESOLUTIONS & STREAM URLS:
─────────────────────────────────────────────────────────────────
 🟢 [ 360P ] : Stream URL from inspection results
 🟢 [ 720P ] : Stream URL from inspection results
═════════════════════════════════════════════════════════════════
```

_The output above is illustrative only. Actual resolutions and URLs depend on the manifest returned by the server._

## Troubleshooting

**`TimeoutError` while waiting for `h1`**

Check that the URL is correct, the page is accessible, and the `h1` element exists. Slow loading or changes to the HTML structure may cause a timeout.

**The `vsembed` iframe cannot be found**

Check whether the page still uses the `vsembed` iframe pattern. If the embed structure has changed, the selectors in the script may need updating.

**The `master.m3u8` URL is not detected**

The player may not have requested the manifest yet, the URL may use a different pattern, or the stream may use another delivery mechanism. The network listener must be registered before the player triggers the manifest request.

**No resolutions are displayed**

Make sure the captured manifest is an HLS master playlist. A media playlist does not necessarily contain `#EXT-X-STREAM-INF` entries.

**The manifest request fails**

The server may require cookies, headers, or a session token. Requests made with `urllib` do not automatically inherit the Chromium browser session.

## Technical Notes

- Resolutions listed in a manifest do not guarantee that every variant is playable.
- Stream URLs may be temporary or require an authenticated session.
- Changes to the page structure or player may require script updates.
- Only inspect content you are authorized to access. Do not bypass authentication or access controls without permission.

---
