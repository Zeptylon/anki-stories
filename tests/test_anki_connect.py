from __future__ import annotations

from unittest.mock import Mock

import pytest
import requests

from anki_stories.anki_connect import AnkiConnectClient, AnkiConnectUnavailableError


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_payload_structure_version_find_cards_and_cards_info(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict] = []

    def fake_post(_url: str, json: dict, timeout: float):
        calls.append({"json": json, "timeout": timeout})
        action = json["action"]
        if action == "version":
            return FakeResponse({"result": 6, "error": None})
        if action == "findCards":
            return FakeResponse({"result": [33, 22], "error": None})
        if action == "cardsInfo":
            return FakeResponse({"result": [{"cardId": 22}], "error": None})
        raise AssertionError(f"Unexpected action: {action}")

    session = requests.Session()
    monkeypatch.setattr(session, "post", fake_post)

    client = AnkiConnectClient(timeout_seconds=4.2)
    client._session = session

    assert client.find_cards('deck:"Demo" rated:7') == [33, 22]
    assert client.cards_info([22]) == [{"cardId": 22}]

    assert calls[0]["json"] == {"action": "version"}
    assert calls[1]["json"] == {
        "action": "findCards",
        "params": {"query": 'deck:"Demo" rated:7'},
        "version": 6,
    }
    assert calls[2]["json"] == {"action": "cardsInfo", "params": {"cards": [22]}, "version": 6}
    assert calls[0]["timeout"] == pytest.approx(4.2)


def test_unreachable_ankiconnect_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    session = requests.Session()
    post = Mock(side_effect=requests.exceptions.ConnectionError("boom"))
    monkeypatch.setattr(session, "post", post)

    client = AnkiConnectClient()
    client._session = session

    with pytest.raises(AnkiConnectUnavailableError) as exc:
        client.get_version()

    message = str(exc.value)
    assert "Start Anki with AnkiConnect enabled" in message
    assert "localhost:8765" in message
