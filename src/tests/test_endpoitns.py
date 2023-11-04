from pathlib import Path
from typing import Iterator

import pytest
from starlette.testclient import TestClient

from app import app
from configuration import AppConfiguration, AppSettings


@pytest.fixture
def test_configuration(testdata_dir: Path) -> AppConfiguration:
    return AppConfiguration(
        settings=AppSettings(
            METADATA_PATH=testdata_dir / "metadata.json",
            RATING_PATH=testdata_dir / "ratings.json",
        ),
        random_seed=1,
    )


@pytest.fixture
def client(test_configuration: AppConfiguration) -> Iterator[TestClient]:
    app.dependency_overrides[AppConfiguration] = lambda: test_configuration
    yield TestClient(app)
    app.dependency_overrides = {}


def test_get_random_song(client: TestClient) -> None:
    res = client.get("/api/songs/random/")
    assert res.status_code == 200
    assert res.json() == dict(
        id="60634790d4629086cc180b012a2083c4",
        title="song two",
        game_title="game two",
    )
