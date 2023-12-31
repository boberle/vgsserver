import json
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from pydantic.v1.json import pydantic_encoder
from starlette.responses import Response

from configuration import AppConfiguration, get_app_configuration
from ratings import InMemoryRatingRepository, PlayedSong
from users import User

api_router = APIRouter()


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
    configuration: AppConfiguration = Depends(get_app_configuration),
) -> User:
    user = configuration.users.get_user(
        username=credentials.username.encode(),
        password=credentials.password.encode(),
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


class SongResponse(BaseModel):
    id: str
    title: Optional[str]
    game_title: Optional[str]
    duration: float
    loop_start: int
    loop_end: int
    path: Path


@api_router.get("/songs/random/")
def _(
    min_duration: Optional[int] = None,
    title_contains: Optional[str] = None,
    game_title_contains: Optional[str] = None,
    min_rating: Optional[int] = None,
    only_has_rating: Optional[bool] = None,
    configuration: AppConfiguration = Depends(get_app_configuration),
    current_user: User = Depends(get_current_user),
) -> SongResponse:
    song = configuration.songs.get_random_song(
        ratings=configuration.get_ratings_for_user(current_user.username),
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
        duration=song.duration,
        loop_start=song.loop_start,
        loop_end=song.loop_end,
        path=song.path,
    )


@api_router.get("/songs/{song_id:str}/file/")
def _(
    song_id: str,
    configuration: AppConfiguration = Depends(get_app_configuration),
    current_user: User = Depends(get_current_user),
) -> Response:
    content = configuration.songs.get_file(song_id)
    return Response(content=content, media_type="application/octet-stream")


class SongPlayRequest(BaseModel):
    timestamp: int
    rating: Literal[0, 1, 2, 3, 4, 5]


class SongPlayResponse(BaseModel):
    rating: Optional[float]


@api_router.post("/songs/{song_id:str}/play/")
def _(
    request: SongPlayRequest,
    song_id: str,
    configuration: AppConfiguration = Depends(get_app_configuration),
    current_user: User = Depends(get_current_user),
) -> SongPlayResponse:
    song = configuration.songs.get_song_by_id(song_id=song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    ratings = configuration.get_ratings_for_user(current_user.username)
    ratings.add_play(
        song_id=song_id,
        song_path=song.path,
        timestamp=request.timestamp,
        rating=request.rating,
    )
    ratings.save()
    return SongPlayResponse(rating=ratings.get_rating(song_id))


@api_router.get("/ratings/export/")
def _(
    configuration: AppConfiguration = Depends(get_app_configuration),
    current_user: User = Depends(get_current_user),
) -> list[PlayedSong]:
    path = configuration.get_ratings_path_for_user(current_user.username)
    if path.exists():
        return InMemoryRatingRepository.load_songs_from_file(path)
    return []


class RatingsImportRequest(BaseModel):
    songs: list[PlayedSong]


@api_router.post("/ratings/import/")
def _(
    request: RatingsImportRequest,
    configuration: AppConfiguration = Depends(get_app_configuration),
    current_user: User = Depends(get_current_user),
) -> Response:
    path = configuration.get_ratings_path_for_user(current_user.username)
    with path.open("w") as fh:
        json.dump(
            [s.model_dump() for s in request.songs],
            fh,
            default=pydantic_encoder,
        )
    return Response()
