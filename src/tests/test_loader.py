from pathlib import Path

from loader import _compute_remote_id, load_metadata, load_ratings
from schema import Play, PlayedSong, Song


def test_loading_metadata(testdata_dir: Path) -> None:
    path = testdata_dir / "metadata.json"
    got = load_metadata(path)
    assert got == {
        _compute_remote_id("abc/one"): Song(
            path=Path("abc/one"),
            timestamp=123,
            loop_start=12,
            loop_end=0,
            duration=1.2,
            size=111,
            title="song one",
            game_title="game one",
            error=False,
            absolute_path=testdata_dir / "abc/one",
            remote_id=_compute_remote_id("abc/one"),
        ),
        _compute_remote_id("abc/two"): Song(
            path=Path("abc/two"),
            timestamp=456,
            loop_start=13,
            loop_end=0,
            duration=21.2,
            size=222,
            title="song two",
            game_title="game two",
            error=False,
            absolute_path=testdata_dir / "abc/two",
            remote_id=_compute_remote_id("abc/two"),
        ),
        _compute_remote_id("abc/three"): Song(
            path=Path("abc/three"),
            timestamp=789,
            loop_start=0,
            loop_end=0,
            duration=3.2,
            size=333,
            title="song three",
            game_title="game three",
            error=True,
            absolute_path=testdata_dir / "abc/three",
            remote_id=_compute_remote_id("abc/three"),
        ),
    }


def test_loading_ratings(testdata_dir: Path) -> None:
    path = testdata_dir / "ratings.json"
    got = load_ratings(path)
    assert got == {
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
