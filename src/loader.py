import json
from pathlib import Path

import pydantic

from schema import Entry, PlayedSong


def load_ratings(file: Path) -> list[PlayedSong]:
    data = json.loads(file.read_text())
    return pydantic.TypeAdapter(list[PlayedSong]).validate_python(data)


def load_metadata(file: Path) -> list[Entry]:
    data = json.loads(file.read_text())
    return pydantic.TypeAdapter(list[Entry]).validate_python(data)
