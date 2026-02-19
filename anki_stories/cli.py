from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass

from anki_stories.anki_connect import (
    DEFAULT_ENDPOINT,
    DEFAULT_TIMEOUT_SECONDS,
    AnkiConnectAPIError,
    AnkiConnectClient,
    AnkiConnectUnavailableError,
)
from anki_stories.output import write_json_output
from anki_stories.service import DeckNotFoundError, fetch_recent_cards

LOGGER = logging.getLogger("anki_stories")


@dataclass(frozen=True)
class CLIArgs:
    deck: str
    days: int
    count: int
    out: str
    field: str | None
    endpoint: str
    timeout: float


def parse_args(argv: list[str] | None = None) -> CLIArgs:
    parser = argparse.ArgumentParser(
        prog="anki-stories",
        description="Fetch recently reviewed Anki cards and write extracted fields to JSON.",
    )
    parser.add_argument("--deck", required=True, help="Anki deck name")
    parser.add_argument("--days", required=True, type=int, help="Lookback window in days (1-31)")
    parser.add_argument("--count", required=True, type=int, help="Number of cards to write")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    parser.add_argument("--field", default=None, help="Optional note field name to extract")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="AnkiConnect endpoint")
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS, help="HTTP timeout in seconds"
    )

    ns = parser.parse_args(argv)

    if not 1 <= ns.days <= 31:
        parser.error("--days must be between 1 and 31.")
    if ns.count < 1:
        parser.error("--count must be >= 1.")
    if not ns.deck.strip():
        parser.error("--deck cannot be empty.")

    return CLIArgs(
        deck=ns.deck,
        days=ns.days,
        count=ns.count,
        out=ns.out,
        field=ns.field,
        endpoint=ns.endpoint,
        timeout=ns.timeout,
    )


def run(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    args = parse_args(argv)

    client = AnkiConnectClient(endpoint=args.endpoint, timeout_seconds=args.timeout)

    try:
        payload = fetch_recent_cards(
            client=client,
            deck=args.deck,
            days=args.days,
            count=args.count,
            field_name=args.field,
        )
        out_path = write_json_output(args.out, payload)
    except (AnkiConnectUnavailableError, DeckNotFoundError, AnkiConnectAPIError) as exc:
        print(f"ERROR: {exc}")
        return 1

    meta = payload["metadata"]
    print(f"Found {meta['count_found']} cards, wrote {meta['count_written']} records to {out_path}")
    return 0
