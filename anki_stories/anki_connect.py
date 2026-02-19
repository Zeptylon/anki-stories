from __future__ import annotations

from dataclasses import dataclass

import requests

DEFAULT_ENDPOINT = "http://127.0.0.1:8765"
DEFAULT_TIMEOUT_SECONDS = 5.0


class AnkiStoriesError(Exception):
    """Base error type for user-facing failures."""


class AnkiConnectUnavailableError(AnkiStoriesError):
    """Raised when AnkiConnect cannot be reached."""


class AnkiConnectAPIError(AnkiStoriesError):
    """Raised when AnkiConnect returns an API error."""


@dataclass
class AnkiConnectClient:
    endpoint: str = DEFAULT_ENDPOINT
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        self._session = requests.Session()
        self._version: int | None = None

    def get_version(self) -> int:
        result = self._raw_call("version", include_version=False)
        if not isinstance(result, int):
            raise AnkiConnectAPIError("AnkiConnect returned an invalid version response.")
        self._version = result
        return result

    def find_cards(self, query: str) -> list[int]:
        result = self._call("findCards", {"query": query})
        if not isinstance(result, list):
            raise AnkiConnectAPIError("AnkiConnect returned invalid data for findCards.")
        return [int(card_id) for card_id in result]

    def cards_info(self, cards: list[int]) -> list[dict]:
        result = self._call("cardsInfo", {"cards": cards})
        if not isinstance(result, list):
            raise AnkiConnectAPIError("AnkiConnect returned invalid data for cardsInfo.")
        return result

    def deck_names(self) -> list[str]:
        result = self._call("deckNames")
        if not isinstance(result, list):
            raise AnkiConnectAPIError("AnkiConnect returned invalid data for deckNames.")
        return [str(name) for name in result]

    def _call(self, action: str, params: dict | None = None):
        if self._version is None:
            self.get_version()
        return self._raw_call(action=action, params=params, include_version=True)

    def _raw_call(self, action: str, params: dict | None = None, include_version: bool = True):
        payload: dict = {"action": action}
        if params is not None:
            payload["params"] = params
        if include_version:
            if self._version is None:
                raise AnkiConnectAPIError("AnkiConnect version was not initialized.")
            payload["version"] = self._version

        try:
            response = self._session.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            raise AnkiConnectUnavailableError(
                f"Could not connect to AnkiConnect at {self.endpoint} (timeout after "
                f"{self.timeout_seconds}s). Start Anki with AnkiConnect enabled and verify "
                "localhost:8765 is reachable."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise AnkiConnectUnavailableError(
                f"Could not connect to AnkiConnect at {self.endpoint}. Start Anki with "
                "AnkiConnect enabled and verify localhost:8765 is reachable."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise AnkiConnectUnavailableError(
                f"Failed to call AnkiConnect at {self.endpoint}: {exc}"
            ) from exc

        data = response.json()
        error = data.get("error")
        if error:
            raise AnkiConnectAPIError(str(error))
        return data.get("result")
