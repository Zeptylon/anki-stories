from __future__ import annotations

import pytest

from anki_stories.cli import parse_args


def test_days_validation_rejects_out_of_range() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--deck", "A", "--days", "0", "--count", "1", "--out", "x.json"])

    with pytest.raises(SystemExit):
        parse_args(["--deck", "A", "--days", "32", "--count", "1", "--out", "x.json"])


def test_count_validation_rejects_non_positive() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--deck", "A", "--days", "7", "--count", "0", "--out", "x.json"])
