import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def testdata_dir() -> Path:
    return Path(__file__).parent / "testdata"


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as dir_name:
        yield Path(dir_name)
