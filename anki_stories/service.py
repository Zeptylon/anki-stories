from __future__ import annotations

from datetime import datetime, timezone

from anki_stories.anki_connect import AnkiConnectAPIError, AnkiConnectClient, AnkiStoriesError
from anki_stories.models import ExtractedCard, JsonDict


class DeckNotFoundError(AnkiStoriesError):
    """Raised when a requested deck cannot be found."""


def build_query(deck: str, days: int) -> str:
    return f'deck:"{deck}" rated:{days}'


def _extract_field(card_info: dict, field_name: str | None) -> tuple[str, str]:
    fields = card_info.get("fields", {})
    if not isinstance(fields, dict) or not fields:
        raise AnkiConnectAPIError(f"Card {card_info.get('cardId')} has no note fields.")

    if field_name:
        field_data = fields.get(field_name)
        if field_data is None:
            raise AnkiConnectAPIError(
                f"Field '{field_name}' not found on card {card_info.get('cardId')}."
            )
        value = field_data.get("value", "")
        return field_name, str(value)

    first_name = next(iter(fields.keys()))
    first_value = fields[first_name].get("value", "")
    return first_name, str(first_value)


def fetch_recent_cards(
    client: AnkiConnectClient,
    deck: str,
    days: int,
    count: int,
    field_name: str | None,
) -> JsonDict:
    try:
        deck_names = set(client.deck_names())
    except AnkiConnectAPIError:
        deck_names = set()

    if deck_names and deck not in deck_names:
        available = ", ".join(sorted(deck_names))
        raise DeckNotFoundError(f'Deck "{deck}" was not found. Available decks: {available}')

    query = build_query(deck=deck, days=days)
    found_ids = client.find_cards(query)
    if not found_ids:
        raise DeckNotFoundError(
            f'No cards found for deck "{deck}" in the last {days} day(s). Query: {query}'
        )

    selected_ids = sorted(found_ids)[:count]
    cards_info = client.cards_info(selected_ids)

    items: list[ExtractedCard] = []
    for card in cards_info:
        used_field_name, value = _extract_field(card, field_name=field_name)
        items.append(
            ExtractedCard(
                card_id=int(card.get("cardId")),
                note_id=int(card.get("note")),
                deck_name=str(card.get("deckName", "")),
                field_name=used_field_name,
                value=value,
            )
        )

    timestamp = datetime.now(timezone.utc).isoformat()  # noqa: UP017
    return {
        "metadata": {
            "timestamp": timestamp,
            "deck": deck,
            "days": days,
            "count_requested": count,
            "count_found": len(found_ids),
            "count_written": len(items),
            "query": query,
            "field_requested": field_name,
            "field_mode": "named" if field_name else "first_field",
        },
        "items": [item.__dict__ for item in items],
    }
