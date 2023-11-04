from pathlib import Path

from songs import InMemorySongRepository, Song
from util import _compute_remote_id


def test_loading_song_repository(testdata_dir: Path) -> None:
    path = testdata_dir / "metadata.json"
    got = InMemorySongRepository.from_file(path)
    assert got.songs == {
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
