# Website

The website is a static hugo site that builds every N hours.


# Event management tool

## Setup

1. Install `uv`
1. `uv sync`
1. `cp .env.example .env` and then edit `.env` with API keys.

You will need Google Cloud credentials.

## Running calendar sync

```bash
# Pull the latest DB
mise run pull
# Run
calsync process
# Push the DB
mise run push
```

## Triggering a remote flow

```bash
mise run trigger
gh run list
gh run watch
```

## Development

```bash
mise run validate
```

## Adding images to the website

Strip ICC color profiles from images before committing. Embedded color profiles (e.g. sRGB) cause the image background to appear as a different shade of white from the page background on iOS/iPadOS Safari with wide-gamut (P3) displays.

```bash
magick input.jpg -strip output.jpg
```