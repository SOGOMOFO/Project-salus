from fastapi import APIRouter

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/")
async def list_memory():
    return {"status": "ok", "entries": []}
