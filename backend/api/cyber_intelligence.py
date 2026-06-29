from fastapi import APIRouter

router = APIRouter(prefix="/cyber_intelligence", tags=["Cyber Intelligence"])

@router.get("/status")
def status():
    return {
        "directorate": "Cyber Intelligence",
        "status": "operational",
        "version": "0.1.0"
    }
