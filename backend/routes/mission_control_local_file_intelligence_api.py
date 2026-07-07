from __future__ import annotations

from fastapi import APIRouter, Query

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/local-file-intelligence")
def api_local_file_intelligence_state():
    return mc_service.get_local_file_intelligence_state()


@router.post("/api/mission-control/local-file-intelligence/reindex")
def api_reindex_local_file_intelligence():
    return mc_service.reindex_local_file_intelligence()


@router.get("/api/mission-control/local-file-intelligence/search")
def api_search_local_file_intelligence(q: str = Query(default=""), limit: int = Query(default=50, ge=1, le=250)):
    return {"status": "ok", "query": q, "results": mc_service.search_local_file_intelligence(q, limit)}
