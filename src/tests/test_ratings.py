import os
from pathlib import Path

import pytest

from ratings import InMemoryRatingRepository, Play, PlayedSong
from util import _compute_remote_id


def test_loading_ratings(testdata_dir: Path) -> None:
    path = testdata_dir / "ratings.json"
    got = InMemoryRatingRepository.from_file(path)
    assert got.ratings == {
        _compute_remote_id("abc/one"): PlayedSong(
            path=Path("abc/one"),
            plays=[
                Play(timestamp=123, rating=1),
                Play(timestamp=456, rating=2),
            ],
        ),
        _compute_remote_id("abc/two"): PlayedSong(
            path=Path("abc/two"),
            plays=[
                Play(timestamp=789, rating=4),
                Play(timestamp=101, rating=5),
            ],
        ),
        _compute_remote_id("abc/three"): PlayedSong(
            path=Path("abc/three"),
            plays=[],
        ),
    }


@pytest.mark.parametrize(
    "prep,exp",
    [
        [{"ratings.json": "abc"}, {"ratings.json.bak1": "abc"}],
        [
            {"ratings.json": "abc", "ratings.json.bak1": "def"},
            {"ratings.json.bak1": "abc", "ratings.json.bak2": "def"},
        ],
        [
            {
                "ratings.json": "abc",
                "ratings.json.bak1": "def",
                "ratings.json.bak2": "ghi",
            },
            {
                "ratings.json.bak1": "abc",
                "ratings.json.bak2": "def",
                "ratings.json.bak3": "ghi",
            },
        ],
        [
            {
                "ratings.json": "abc",
                "ratings.json.bak1": "def",
                "ratings.json.bak2": "ghi",
                "ratings.json.bak3": "jkl",
            },
            {
                "ratings.json.bak1": "abc",
                "ratings.json.bak2": "def",
                "ratings.json.bak3": "ghi",
            },
        ],
    ],
)
def test_backup(
    temp_directory: Path, prep: dict[str, str], exp: dict[str, str]
) -> None:
    for fname, content in prep.items():
        (temp_directory / fname).write_text(content)

    fname = next(iter(prep.keys()))
    rep = InMemoryRatingRepository(
        ratings=dict(), file=(temp_directory / fname), number_of_backup_files=3
    )
    rep.backup_file()

    got: dict[str, str] = dict()
    for fname in os.listdir(temp_directory):
        got[fname] = (temp_directory / fname).read_text()

    assert got == exp
