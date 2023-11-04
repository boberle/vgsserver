from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from random import Random
from typing import Optional

import pydantic
from pydantic import BaseModel

from ratings import RatingRepository
from util import _compute_remote_id


class MetadataEntry(BaseModel):
    path: Path
    timestamp: int
    loop_start: int = 0  # microseconds
    loop_end: int = 0  # microseconds
    duration: float = 0.0  # seconds
    size: int = 0  # bytes
    title: Optional[str] = None
    game_title: Optional[str] = None
    error: bool = False


class Song(MetadataEntry):
    absolute_path: Path
    remote_id: str


class SongRepository(ABC):
    @abstractmethod
    def get_random_song(
        self,
        ratings: RatingRepository,
        min_duration: Optional[int] = None,
        title_contains: Optional[str] = None,
        game_title_contains: Optional[str] = None,
        min_rating: Optional[int] = None,
        only_has_rating: Optional[bool] = None,
        only_has_no_rating: Optional[bool] = None,
    ) -> Optional[Song]:
        ...  # pragma:nocover


@dataclass
class InMemorySongRepository(SongRepository):
    songs: dict[str, Song]
    random: Random = field(default_factory=Random)

    def get_random_song(
        self,
        ratings: RatingRepository,
        min_duration: Optional[int] = None,
        title_contains: Optional[str] = None,
        game_title_contains: Optional[str] = None,
        min_rating: Optional[int] = None,
        only_has_rating: Optional[bool] = None,
        only_has_no_rating: Optional[bool] = None,
    ) -> Optional[Song]:
        ids = list(self.songs.keys())
        self.random.shuffle(ids)
        for id in ids:
            song = self.songs[id]
            if min_duration is not None and song.duration < min_duration:
                continue
            if (
                title_contains is not None
                and song.title is not None
                and title_contains not in song.title
            ):
                continue
            if (
                game_title_contains is not None
                and song.game_title is not None
                and game_title_contains not in song.game_title
            ):
                continue
            if only_has_rating and ratings.song_has_no_rating(song.remote_id):
                continue
            if only_has_no_rating and ratings.song_has_rating(song.remote_id):
                continue
            if min_rating is not None and ratings.song_has_rating(song.remote_id):
                song_rating = ratings.get_rating(song.remote_id)
                if song_rating is not None and song_rating < min_rating:
                    continue
            return song
        return None

    @staticmethod
    def from_file(
        file: Path, random: Optional[Random] = None
    ) -> InMemorySongRepository:
        data = json.loads(file.read_text())
        entries = pydantic.TypeAdapter(list[MetadataEntry]).validate_python(data)

        def make_song(e: MetadataEntry) -> tuple[str, Song]:
            id = _compute_remote_id(e.path)
            song = Song(
                **e.model_dump(),
                absolute_path=Path(file.parent / e.path),
                remote_id=_compute_remote_id(e.path),
            )
            return id, song

        if not random:
            random = Random()
        return InMemorySongRepository(
            songs=dict(make_song(e) for e in entries),
            random=random,
        )
