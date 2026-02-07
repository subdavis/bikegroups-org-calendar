## Setup

1. Install `uv`
1. `uv sync`
1. `cp .env.example .env` and update.

You will need Google Cloud credentials.

## Running the tool

```bash
# Pull the latest DB
mise run pull
# Run
mise run sync
# Push the DB
mise run push
```
