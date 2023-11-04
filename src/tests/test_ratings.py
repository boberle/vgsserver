from pathlib import Path

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
