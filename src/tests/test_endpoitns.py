import base64
from pathlib import Path
from typing import Iterator

import pytest
from starlette.testclient import TestClient

from app import app
from configuration import AppConfiguration, AppSettings, get_app_configuration


@pytest.fixture
def test_configuration(testdata_dir: Path) -> AppConfiguration:
    return AppConfiguration(
        settings=AppSettings(
            METADATA_PATH=testdata_dir / "metadata.json",
            RATING_PATH=testdata_dir / "ratings.json",
            USER_PATH=testdata_dir / "users.json",
        ),
        random_seed=1,
    )


@pytest.fixture
def client(test_configuration: AppConfiguration) -> Iterator[TestClient]:
    app.dependency_overrides[get_app_configuration] = lambda: test_configuration
    yield TestClient(app)
    app.dependency_overrides = {}


@pytest.fixture
def authorization_header() -> str:
    authorization_header = (
        "Basic " + base64.b64encode("testuser:password".encode()).decode()
    )
    return authorization_header


def test_get_random_song__not_authenticated(client: TestClient) -> None:
    res = client.get("/api/songs/random/")
    assert res.status_code == 401
    assert res.json() == {"detail": "Not authenticated"}


def test_get_random_song(client: TestClient, authorization_header: str) -> None:
    res = client.get(
        "/api/songs/random/", headers={"Authorization": authorization_header}
    )
    assert res.status_code == 200
    assert res.json() == dict(
        id="60634790d4629086cc180b012a2083c4",
        title="song two",
        game_title="game two",
    )


def test_get_song_file__not_authenticated(client: TestClient) -> None:
    res = client.get("/api/songs/60634790d4629086cc180b012a2083c4/file/")
    assert res.status_code == 401
    assert res.json() == {"detail": "Not authenticated"}


def test_get_song_file(client: TestClient, authorization_header: str) -> None:
    res = client.get(
        "/api/songs/60634790d4629086cc180b012a2083c4/file/",
        headers={"Authorization": authorization_header},
    )
    assert res.status_code == 200
    assert res.content == b"content two"
