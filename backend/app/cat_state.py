from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from random import choice
from typing import Any

STATUS_MIN = 0
STATUS_MAX = 10
COLOR_PATTERNS = ("black", "calico", "colorpoint", "tabby", "white")


def _clamp(value: int) -> int:
    return max(STATUS_MIN, min(STATUS_MAX, value))


@dataclass
class CatState:
    name: str = "Unnamed Cat"
    energy: int = 6
    happiness: int = 6
    cleanliness: int = 6
    age: int = 2
    color_pattern: str | None = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        self.updated_at = datetime.now()

    def feed(self, amount: int = 3) -> None:
        self.energy = _clamp(self.energy + amount)
        self.happiness = _clamp(self.happiness + 1)
        # Randomly deduct cleanliness on feed. Randomness makes it possible
        # for the cat status to reach 10 / 10 / 10.
        if choice([True, False]):
            self.cleanliness = _clamp(self.cleanliness - 1)
        self.touch()

    def play(self, boost: int = 2) -> None:
        self.happiness = _clamp(self.happiness + boost)
        self.energy = _clamp(self.energy - 1)
        # Randomly deduct cleanliness on play. Randomness makes it possible
        # for the cat status to reach 10 / 10 / 10.
        if choice([True, False]):
            self.cleanliness = _clamp(self.cleanliness - 1)
        self.touch()

    def clean(self, boost: int = 3) -> None:
        self.cleanliness = _clamp(self.cleanliness + boost)
        # Randomly deduct happiness on clean. Randomness makes it possible
        # for the cat status to reach 10 / 10 / 10.
        if choice([True, False]):
            self.happiness = _clamp(self.happiness - 1)
        self.touch()

    def rename(self, value: str) -> None:
        print(f"Renaming cat to {value}")
        self.name = value
        if not self.color_pattern:
            print(f"Choosing random color pattern for {value}")
            self.color_pattern = choice(COLOR_PATTERNS)
            print(f"Color pattern: {self.color_pattern}")
        self.touch()

    def set_age(self, value: int | None) -> None:
        if value and isinstance(value, int):
            self.age = min(max(value, 1), 15)
            self.touch()

    def clone(self) -> "CatState":
        return replace(self)

    def to_payload(self, thread_id: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "energy": self.energy,
            "happiness": self.happiness,
            "cleanliness": self.cleanliness,
            "age": self.age,
            "colorPattern": self.color_pattern,
            "updatedAt": self.updated_at.isoformat(),
        }
        if thread_id:
            payload["threadId"] = thread_id
        return payload
