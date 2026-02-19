from __future__ import annotations

import pytest

from anki_stories.anki_connect import AnkiConnectAPIError
from anki_stories.service import build_query, fetch_recent_cards


class StubClient:
    def __init__(self, decks: list[str], card_ids: list[int], cards_info_payload: list[dict]):
        self._decks = decks
        self._card_ids = card_ids
        self._cards_info_payload = cards_info_payload
        self.query_seen: str | None = None
        self.ids_seen: list[int] | None = None

    def deck_names(self) -> list[str]:
        return self._decks

    def find_cards(self, query: str) -> list[int]:
        self.query_seen = query
        return self._card_ids

    def cards_info(self, cards: list[int]) -> list[dict]:
        self.ids_seen = cards
        return self._cards_info_payload


def test_build_query_expected_string() -> None:
    assert build_query("My Deck", 7) == 'deck:"My Deck" rated:7'


def test_fetch_recent_cards_uses_deterministic_selection_and_default_first_field() -> None:
    client = StubClient(
        decks=["My Deck"],
        card_ids=[50, 10, 20],
        cards_info_payload=[
            {
                "cardId": 10,
                "note": 1001,
                "deckName": "My Deck",
                "fields": {"Front": {"value": "猫"}, "Back": {"value": "cat"}},
            },
            {
                "cardId": 20,
                "note": 1002,
                "deckName": "My Deck",
                "fields": {"Front": {"value": "犬"}, "Back": {"value": "dog"}},
            },
        ],
    )

    payload = fetch_recent_cards(client, deck="My Deck", days=7, count=2, field_name=None)

    assert client.query_seen == 'deck:"My Deck" rated:7'
    assert client.ids_seen == [10, 20]
    assert payload["metadata"]["count_found"] == 3
    assert payload["metadata"]["count_written"] == 2
    assert payload["items"][0]["field_name"] == "Front"


def test_fetch_recent_cards_extracts_named_field() -> None:
    client = StubClient(
        decks=["My Deck"],
        card_ids=[7],
        cards_info_payload=[
            {
                "cardId": 7,
                "note": 777,
                "deckName": "My Deck",
                "fields": {"Expression": {"value": "ありがとう"}, "Meaning": {"value": "thanks"}},
            }
        ],
    )

    payload = fetch_recent_cards(client, deck="My Deck", days=3, count=1, field_name="Meaning")
    assert payload["items"][0]["field_name"] == "Meaning"
    assert payload["items"][0]["value"] == "thanks"


def test_fetch_recent_cards_missing_named_field_raises() -> None:
    client = StubClient(
        decks=["My Deck"],
        card_ids=[7],
        cards_info_payload=[
            {
                "cardId": 7,
                "note": 777,
                "deckName": "My Deck",
                "fields": {"Expression": {"value": "ありがとう"}},
            }
        ],
    )

    with pytest.raises(AnkiConnectAPIError):
        fetch_recent_cards(client, deck="My Deck", days=3, count=1, field_name="Meaning")
