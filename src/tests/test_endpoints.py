import base64
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Iterator

import pytest
from starlette.testclient import TestClient

from app import app
from configuration import AppConfiguration, AppSettings, get_app_configuration
from ratings import InMemoryRatingRepository


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as dir_name:
        yield Path(dir_name)


@pytest.fixture
def test_configuration(testdata_dir: Path, temp_directory: Path) -> AppConfiguration:
    rating_dir = temp_directory / "ratings"
    (rating_dir / "testuser").mkdir(exist_ok=False, parents=True)
    shutil.copy2(testdata_dir / "ratings.json", rating_dir / "testuser")
    return AppConfiguration(
        settings=AppSettings(
            METADATA_PATH=testdata_dir / "metadata.json",
            RATING_DIR_PATH=rating_dir,
            USER_PATH=testdata_dir / "users.json",
        ),
        random_seed=1,
    )


@pytest.fixture
def client_with_configuration(
    test_configuration: AppConfiguration,
) -> Iterator[tuple[AppConfiguration, TestClient]]:
    app.dependency_overrides[get_app_configuration] = lambda: test_configuration
    yield test_configuration, TestClient(app)
    app.dependency_overrides = {}


@pytest.fixture
def client(
    client_with_configuration: tuple[AppConfiguration, TestClient]
) -> TestClient:
    return client_with_configuration[1]


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
        loop_start=13,
        loop_end=0,
        path="abc/two",
        duration=21.2,
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


def test_add_play__not_authenticated(client: TestClient) -> None:
    res = client.post("/api/songs/60634790d4629086cc180b012a2083c4/play/")
    assert res.status_code == 401
    assert res.json() == {"detail": "Not authenticated"}


def test_add_play(
    client_with_configuration: tuple[AppConfiguration, TestClient],
    authorization_header: str,
) -> None:
    conf, client = client_with_configuration
    res = client.post(
        "/api/songs/60634790d4629086cc180b012a2083c4/play/",
        headers={"Authorization": authorization_header},
        json=dict(
            timestamp=123,
            rating=2,
        ),
    )
    assert res.status_code == 200
    assert res.json() == {"rating": 3.6666666666666665}

    assert (
        conf.get_ratings_for_user("testuser").get_rating(
            "60634790d4629086cc180b012a2083c4"
        )
        == 3.6666666666666665
    )

    new_ratings = InMemoryRatingRepository.from_file(
        conf.settings.RATING_DIR_PATH / "testuser" / "ratings.json"
    )
    assert (
        new_ratings.get_rating("60634790d4629086cc180b012a2083c4") == 3.6666666666666665
    )


def test_add_play__invalid_rating(
    client: TestClient,
    authorization_header: str,
) -> None:
    res = client.post(
        "/api/songs/60634790d4629086cc180b012a2083c4/play/",
        headers={"Authorization": authorization_header},
        json=dict(
            timestamp=123,
            rating=10,
        ),
    )
    assert res.status_code == 422
