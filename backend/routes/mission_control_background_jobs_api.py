from __future__ import annotations

from fastapi import APIRouter

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/background-jobs")
def api_background_job_state():
    return mc_service.get_background_job_state()


@router.get("/api/mission-control/background-jobs/runs")
def api_background_job_runs():
    return {
        "status": "ok",
        "runs": mc_service.list_background_job_runs(),
    }


@router.post("/api/mission-control/background-jobs/{job_key}/run")
def api_run_background_job(job_key: str):
    return mc_service.run_background_job(job_key, actor="api")


@router.post("/api/mission-control/background-jobs/{job_key}/enable")
def api_enable_background_job(job_key: str):
    job = mc_service.set_background_job_enabled(job_key, True, actor="api")
    return {
        "status": "enabled" if job.get("job_key") else job.get("status"),
        "job": job,
    }


@router.post("/api/mission-control/background-jobs/{job_key}/disable")
def api_disable_background_job(job_key: str):
    job = mc_service.set_background_job_enabled(job_key, False, actor="api")
    return {
        "status": "disabled" if job.get("job_key") else job.get("status"),
        "job": job,
    }


@router.post("/api/mission-control/background-jobs/sweep")
def api_background_job_sweep():
    return mc_service.run_background_job_sweep(actor="api")
