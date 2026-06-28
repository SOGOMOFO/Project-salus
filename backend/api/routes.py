from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def home():
    return {
        "project": "Project Salus",
        "status": "Operational",
        "module": "Mission Control",
        "version": "1.0.0"
    }

@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }

@router.get("/missions")
async def missions():
    return {
        "missions": []
    }
