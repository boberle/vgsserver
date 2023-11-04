from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import pydantic
from pydantic import BaseModel
from pydantic.v1.json import pydantic_encoder

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

    @abstractmethod
    def add_play(
        self,
        song_id: str,
        song_path: Path,
        timestamp: int,
        rating: Literal[1, 2, 3, 4, 5],
    ) -> None:
        ...  # pragma:nocover

    @abstractmethod
    def save(self) -> None:
        ...  # pragma:nocover


class Play(BaseModel):
    timestamp: int
    rating: Literal[1, 2, 3, 4, 5]


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
    file: Optional[Path] = None

    def get_rating(self, song_id: str) -> Optional[float]:
        if song_id in self.ratings:
            played_song = self.ratings[song_id]
            return played_song.rating
        return None

    def song_has_rating(self, song_id: str) -> bool:
        return song_id in self.ratings and self.ratings[song_id].rating is not None

    def song_has_no_rating(self, song_id: str) -> bool:
        return not self.song_has_rating(song_id)

    def add_play(
        self,
        song_id: str,
        song_path: Path,
        timestamp: int,
        rating: Literal[1, 2, 3, 4, 5],
    ) -> None:
        played_song = self.ratings.get(song_id)
        play = Play(timestamp=timestamp, rating=rating)
        if played_song is not None:
            played_song.plays.append(play)
        else:
            self.ratings[song_id] = PlayedSong(
                path=song_path,
                plays=[play],
            )

    def save(self) -> None:
        if self.file is not None:
            with self.file.open("w") as fh:
                json.dump(
                    [s.model_dump() for s in self.ratings.values()],
                    fh,
                    default=pydantic_encoder,
                )

    @staticmethod
    def from_file(file: Path) -> InMemoryRatingRepository:
        data = json.loads(file.read_text())
        played_songs = pydantic.TypeAdapter(list[PlayedSong]).validate_python(data)
        return InMemoryRatingRepository(
            ratings={_compute_remote_id(p.path): p for p in played_songs},
            file=file,
        )
