import hashlib
from typing import Any


def _compute_remote_id(data: Any) -> str:
    return hashlib.md5(str(data).encode()).hexdigest()
