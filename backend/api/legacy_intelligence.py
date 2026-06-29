from fastapi import APIRouter

router = APIRouter(prefix="/legacy_intelligence", tags=["Legacy Intelligence"])


@router.get("/status")
def status():
    return {
        "directorate": "Legacy Intelligence",
        "status": "operational",
        "version": "0.1.0",
    }
