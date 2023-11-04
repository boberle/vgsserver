from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from configuration import AppConfiguration, get_app_configuration
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
