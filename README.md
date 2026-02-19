# anki-stories

Fetch recently reviewed Anki cards and save extracted note fields to JSON.

## Setup

```bash
./scripts/dev_setup.sh
source .venv/bin/activate
```

## Usage

Main entrypoint (kept for compatibility):

```bash
python Main.py --deck "<my deck>" --days 7 --count 50 --out ./outputs/recent.json
```

Equivalent module entrypoint:

```bash
python -m anki_stories --deck "<my deck>" --days 7 --count 50 --out ./outputs/recent.json
```

Optional field selection:

```bash
python Main.py --deck "Japanese::Core2k" --days 7 --count 50 --out ./outputs/recent.json --field Expression
```

The output file contains metadata (deck, days, count, timestamp, query) and extracted values.
