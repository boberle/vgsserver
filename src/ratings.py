from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import pydantic
from pydantic import BaseModel

from util import _compute_remote_id


class RatingRepository(ABC):
    @abstractmethod
    def get_rating(self, song_id: str) -> Optional[float]:
        ...  # pragma:nocover

    @abstractmethod
    def song_has_rating(self, song_id: str) -> bool:
        ...  # pragma:nocover

    @abstractmethod
    def song_has_no_rating(self, song_id: str) -> bool:
        ...  # pragma:nocover


class Play(BaseModel):
    timestamp: int
    rating: Literal[0, 1, 2, 3, 4, 5]


class PlayedSong(BaseModel):
    path: Path
    plays: list[Play]

    @property
    def rating(self) -> Optional[float]:
        if len(self.plays) == 0:
            return None
        return sum([p.rating for p in self.plays]) / len(self.plays)


@dataclass
class InMemoryRatingRepository(RatingRepository):
    ratings: dict[str, PlayedSong]

    def get_rating(self, song_id: str) -> Optional[float]:
        if song_id in self.ratings:
            played_song = self.ratings[song_id]
            return played_song.rating
        return None

    def song_has_rating(self, song_id: str) -> bool:
        return song_id in self.ratings and self.ratings[song_id].rating is not None

    def song_has_no_rating(self, song_id: str) -> bool:
        return not self.song_has_rating(song_id)

    @staticmethod
    def from_file(file: Path) -> InMemoryRatingRepository:
        data = json.loads(file.read_text())
        played_songs = pydantic.TypeAdapter(list[PlayedSong]).validate_python(data)
        return InMemoryRatingRepository(
            {_compute_remote_id(p.path): p for p in played_songs}
        )
