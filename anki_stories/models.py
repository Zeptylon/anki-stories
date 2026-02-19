from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExtractedCard:
    card_id: int
    note_id: int
    deck_name: str
    field_name: str
    value: str


JsonDict = dict[str, Any]
