from pathlib import Path

from loader import load_metadata, load_ratings
from schema import Entry, Play, PlayedSong


def test_loading_metadata(testdata_dir: Path) -> None:
    path = testdata_dir / "metadata.json"
    got = load_metadata(path)
    assert got == [
        Entry(
            path=Path("abc/one"),
            timestamp=123,
            loop_start=12,
            loop_end=0,
            duration=1.2,
            size=111,
            title="song one",
            game_title="game one",
            error=False,
        ),
        Entry(
            path=Path("abc/two"),
            timestamp=456,
            loop_start=13,
            loop_end=0,
            duration=21.2,
            size=222,
            title="song two",
            game_title="game two",
            error=False,
        ),
        Entry(
            path=Path("abc/three"),
            timestamp=789,
            loop_start=0,
            loop_end=0,
            duration=3.2,
            size=333,
            title="song three",
            game_title="game three",
            error=True,
        ),
    ]


def test_loading_ratings(testdata_dir: Path) -> None:
    path = testdata_dir / "ratings.json"
    got = load_ratings(path)
    assert got == [
        PlayedSong(
            path=Path("abc/one"),
            plays=[
                Play(timestamp=123, rating=1),
                Play(timestamp=456, rating=2),
            ],
        ),
        PlayedSong(
            path=Path("abc/two"),
            plays=[
                Play(timestamp=789, rating=4),
                Play(timestamp=101, rating=5),
            ],
        ),
        PlayedSong(
            path=Path("abc/three"),
            plays=[],
        ),
    ]
