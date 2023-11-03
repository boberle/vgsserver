from pathlib import Path

import pytest


@pytest.fixture
def testdata_dir() -> Path:
    return Path(__file__).parent / "testdata"
