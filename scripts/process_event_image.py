#!/usr/bin/env python3
"""Process an event image upload issue: parse, download, and save images."""

import os
import re
import sys
from pathlib import Path

import httpx

REPO = os.environ.get("REPO", "")
ISSUE_NUMBER = os.environ.get("ISSUE_NUMBER", "")
ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
ISSUE_AUTHOR = os.environ.get("ISSUE_AUTHOR", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

ASSET_DIR = Path("website/assets/event-images")

CONTENT_TYPE_TO_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/avif": "avif",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
}


def parse_event_id(body: str) -> str:
    match = re.search(r"### Event ID\s*\n\n([^\n]+)", body)
    if not match:
        print(
            "ERROR: Could not find '### Event ID' section in issue body.",
            file=sys.stderr,
        )
        sys.exit(1)
    event_id = match.group(1).strip()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", event_id):
        print(
            f"ERROR: Event ID '{event_id}' contains invalid characters. "
            "Only alphanumeric characters, hyphens, and underscores are allowed.",
            file=sys.stderr,
        )
        sys.exit(1)
    return event_id


def parse_image_urls(body: str) -> list[str]:
    pattern = r"!\[.*?\]\((https://(?:github\.com/user-attachments/assets/|user-images\.githubusercontent\.com/)\S+)\)"
    return re.findall(pattern, body)


def find_next_index(event_id: str) -> int:
    existing = list(ASSET_DIR.glob(f"{event_id}.*"))
    if not existing:
        return 1
    indices = []
    for p in existing:
        # filename: event_id.N.ext
        parts = p.stem.split(".")
        if len(parts) >= 2:
            try:
                indices.append(int(parts[-1]))
            except ValueError:
                pass
    return max(indices, default=0) + 1


def download_image(url: str, dest: Path) -> Path:
    with httpx.Client(follow_redirects=True, timeout=30) as client:
        response = client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").split(";")[0].strip()
        ext = CONTENT_TYPE_TO_EXT.get(content_type)
        if not ext:
            # Fall back to guessing from URL
            url_path = url.split("?")[0]
            suffix = Path(url_path).suffix.lstrip(".")
            ext = suffix if suffix else "bin"
        final_dest = dest.with_suffix(f".{ext}")
        final_dest.write_bytes(response.content)
        return final_dest


def main():
    if not ISSUE_BODY:
        print("ERROR: ISSUE_BODY environment variable is empty.", file=sys.stderr)
        sys.exit(1)

    event_id = parse_event_id(ISSUE_BODY)
    image_urls = parse_image_urls(ISSUE_BODY)

    if not image_urls:
        print(
            "ERROR: No image URLs found in issue body. "
            "Make sure to attach images using GitHub's drag-and-drop or paste feature.",
            file=sys.stderr,
        )
        sys.exit(1)

    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    next_index = find_next_index(event_id)
    created_files = []

    for i, url in enumerate(image_urls):
        index = next_index + i
        # Placeholder path without extension; download_image will add the right extension
        dest_stem = ASSET_DIR / f"{event_id}.{index}"
        try:
            final_path = download_image(url, dest_stem)
            created_files.append(str(final_path))
        except Exception as e:
            print(f"ERROR: Failed to download image {url}: {e}", file=sys.stderr)
            sys.exit(1)

    for path in created_files:
        print(path)


if __name__ == "__main__":
    main()
