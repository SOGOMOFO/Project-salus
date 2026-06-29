from fastapi import APIRouter
from backend.engineering.builder import get_builder_status

router = APIRouter(
    prefix="/engineering",
    tags=["Engineering"],
)

@router.get("/status")
def engineering_status():
    return get_builder_status()
