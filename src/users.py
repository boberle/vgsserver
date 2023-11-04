from __future__ import annotations

import json
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import bcrypt
import pydantic
from pydantic import BaseModel


@dataclass
class User:
    username: str


class UserData(BaseModel):
    username: bytes
    password_hash: bytes


class UserRepository(ABC):
    @abstractmethod
    def get_user(self, username: bytes, password: bytes) -> Optional[User]:
        ...  # pragma:nocover


@dataclass
class InMemoryUserRepository(UserRepository):
    users: list[UserData]

    def get_user(self, username: bytes, password: bytes) -> Optional[User]:
        for user in self.users:
            if secrets.compare_digest(username, user.username) and check_password(
                password, user.password_hash
            ):
                return User(username=user.username.decode())
        return None

    @staticmethod
    def from_file(file: Path) -> InMemoryUserRepository:
        data = json.loads(file.read_text())
        users = pydantic.TypeAdapter(list[UserData]).validate_python(data)
        return InMemoryUserRepository(users=users)


def hash_password(password: bytes) -> bytes:
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password, salt)
    return password_hash


def check_password(user_password: bytes, password_hash: bytes) -> bool:
    return bcrypt.checkpw(user_password, password_hash)
