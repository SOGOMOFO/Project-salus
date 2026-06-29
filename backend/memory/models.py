from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryEntry:
    key: str
    value: Any
    category: str = "general"
