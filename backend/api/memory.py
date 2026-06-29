import os

from fastapi import APIRouter, Header, Request, HTTPException

from backend.memory.memory_engine import add_memory, delete_memory, list_memories, search_memories
from backend.memory.models import MemoryCreateRequest

router = APIRouter()

SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")


def verify_passphrase(x_salus_passphrase: str | None):
    if x_salus_passphrase != SALUS_PASSPHRASE:
        raise HTTPException(status_code=401, detail="Unauthorized access denied")


@router.get("/memory")
async def get_memories(x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)
    return {"status": "ok", "memories": list_memories()}


@router.post("/memory")
async def create_memory(request: Request, x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)
    payload = await request.json()
    model = MemoryCreateRequest(**payload)
    memory = add_memory(
        memory_type=model.memory_type,
        title=model.title,
        content=model.content,
        tags=model.tags or [],
        source=model.source,
    )
    return {"status": "created", "memory": memory}


@router.get("/memory/search")
async def search_memory(query: str, x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)
    return {"status": "ok", "memories": search_memories(query)}


@router.delete("/memory/{memory_id}")
async def delete_memory_route(memory_id: int, x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)
    deleted = delete_memory(memory_id)
    return {"status": "deleted" if deleted else "not_found", "id": memory_id}
