from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel


class Entry(BaseModel):
    path: Path
    timestamp: int
    loop_start: int = 0  # microseconds
    loop_end: int = 0  # microseconds
    duration: float = 0.0  # seconds
    size: int = 0  # bytes
    title: Optional[str] = None
    game_title: Optional[str] = None
    error: bool = False


class Play(BaseModel):
    timestamp: int
    rating: Literal[0, 1, 2, 3, 4, 5]


class PlayedSong(BaseModel):
    path: Path
    plays: list[Play]
