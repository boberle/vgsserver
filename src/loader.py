import hashlib
import json
from pathlib import Path
from typing import Any

import pydantic

from schema import MetadataEntry, PlayedSong, Ratings, Song, SongCollection


def load_ratings(file: Path) -> Ratings:
    data = json.loads(file.read_text())
    played_songs = pydantic.TypeAdapter(list[PlayedSong]).validate_python(data)
    return {_compute_remote_id(p.path): p for p in played_songs}


def load_metadata(file: Path) -> SongCollection:
    data = json.loads(file.read_text())
    entries = pydantic.TypeAdapter(list[MetadataEntry]).validate_python(data)

    def make_song(e: MetadataEntry) -> tuple[str, Song]:
        id = _compute_remote_id(e.path)
        song = Song(
            **e.model_dump(),
            absolute_path=Path(file.parent / e.path),
            remote_id=_compute_remote_id(e.path)
        )
        return id, song

    return dict(make_song(e) for e in entries)


def _compute_remote_id(data: Any) -> str:
    return hashlib.md5(str(data).encode()).hexdigest()
