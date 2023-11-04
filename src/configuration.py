from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from ratings import InMemoryRatingRepository, RatingRepository
from songs import InMemorySongRepository, SongRepository


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VGSSERVER_")

    METADATA_PATH: Path = Path("/songs/metadata.json")
    RATING_PATH: Path = Path("/ratings.json")


@dataclass
class AppConfiguration:
    settings: AppSettings
    random_seed: Optional[int] = None

    @property
    def songs(self) -> SongRepository:
        return InMemorySongRepository.from_file(
            self.settings.METADATA_PATH,
            random=self.random,
        )

    @property
    def ratings(self) -> RatingRepository:
        return InMemoryRatingRepository.from_file(self.settings.RATING_PATH)

    @property
    def random(self) -> Random:
        return Random(self.random_seed)


_app_configuration = AppConfiguration(settings=AppSettings())


def get_app_configuration() -> AppConfiguration:
    return _app_configuration
