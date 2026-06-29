from typing import Optional

from pydantic import BaseModel, Field, field_validator

SUPPORTED_MEMORY_TYPES = {"user", "project", "agent", "mission", "legacy"}


class MemoryCreateRequest(BaseModel):
    memory_type: str = Field(default="legacy")
    title: str = Field(default="")
    content: str = Field(default="")
    tags: Optional[list[str]] = Field(default_factory=list)
    source: Optional[str] = None
    session_id: Optional[str] = None
    importance: Optional[float] = None

    @field_validator("memory_type")
    @classmethod
    def validate_memory_type(cls, value: str) -> str:
        if value not in SUPPORTED_MEMORY_TYPES:
            return "legacy"
        return value


class MemoryRecord(BaseModel):
    id: int
    memory_type: str
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    source: Optional[str] = None
    importance: float = 0.5
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
