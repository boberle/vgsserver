from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from configuration import AppConfiguration

api_router = APIRouter()


class SongResponse(BaseModel):
    id: str
    title: Optional[str]
    game_title: Optional[str]


@api_router.get("/songs/random/")
def _(
    min_duration: Optional[int] = None,
    title_contains: Optional[str] = None,
    game_title_contains: Optional[str] = None,
    min_rating: Optional[int] = None,
    only_has_rating: Optional[bool] = None,
    configuration: AppConfiguration = Depends(AppConfiguration),
) -> SongResponse:
    song = configuration.songs.get_random_song(
        ratings=configuration.ratings,
        min_duration=min_duration,
        title_contains=title_contains,
        game_title_contains=game_title_contains,
        min_rating=min_rating,
        only_has_rating=only_has_rating,
    )
    if song is None:
        raise HTTPException(404, "No song found")
    return SongResponse(
        id=song.remote_id,
        title=song.title,
        game_title=song.game_title,
    )
