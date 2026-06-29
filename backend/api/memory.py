import os

from fastapi import APIRouter, Header, Request, HTTPException

from backend.memory.memory_engine import add_memory, delete_memory, list_memories, search_memories
from backend.memory.models import MemoryCreateRequest
from backend.memory.search import semantic_search_memories
from backend.memory.session import SessionMemoryStore
from backend.security.core import security_core

router = APIRouter()
session_store = SessionMemoryStore()

SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")


def verify_passphrase(x_salus_passphrase: str | None):
    security_core.authorize(
        action="memory.legacy",
        x_salus_passphrase=x_salus_passphrase,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )


@router.get("/memory")
async def get_memories(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="memory.read",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return {"status": "ok", "memories": list_memories()}


@router.post("/memory")
async def create_memory(
    request: Request,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="memory.create",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent"},
    )
    payload = await request.json()
    model = MemoryCreateRequest(**payload)
    memory = add_memory(
        memory_type=model.memory_type,
        title=model.title,
        content=model.content,
        tags=model.tags or [],
        source=model.source,
        importance=model.importance,
    )
    if model.session_id:
        session_store.set(model.session_id, f"memory:{memory['id']}", memory["content"])
    return {"status": "created", "memory": memory}


@router.get("/memory/search")
async def search_memory(
    query: str,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="memory.search",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return {"status": "ok", "memories": search_memories(query)}


@router.get("/memory/semantic-search")
async def semantic_search_memory(
    query: str,
    limit: int = 10,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="memory.semantic_search",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    matches = semantic_search_memories(query, list_memories(), limit=limit)
    return {"status": "ok", "memories": matches}


@router.get("/memory/session/{session_id}")
async def list_session_memory(
    session_id: str,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="memory.session.read",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return {"status": "ok", "session_id": session_id, "memories": session_store.list(session_id)}


@router.post("/memory/session/{session_id}")
async def set_session_memory(
    session_id: str,
    request: Request,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="memory.session.create",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent"},
    )
    payload = await request.json()
    if not isinstance(payload, dict):
        payload = {}
    key = str(payload.get("key", "")).strip()
    value = str(payload.get("value", ""))
    if not key:
        raise HTTPException(status_code=400, detail="key is required")
    record = session_store.set(session_id, key, value)
    return {"status": "created", "memory": record}


@router.delete("/memory/session/{session_id}")
async def clear_session_memory(
    session_id: str,
    key: str | None = None,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="memory.session.delete",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent"},
    )
    removed = session_store.delete(session_id, key)
    return {"status": "deleted", "removed": removed, "session_id": session_id}


@router.delete("/memory/{memory_id}")
async def delete_memory_route(
    memory_id: int,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="memory.delete",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent"},
    )
    deleted = delete_memory(memory_id)
    return {"status": "deleted" if deleted else "not_found", "id": memory_id}
