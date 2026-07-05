from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.build_accelerator_service import (
    CORE_MODULES,
    NEXT_BUILD_CANDIDATES,
    build_commit_pack,
    build_release_checklist,
    build_smoke_test_plan,
    build_sprint,
    build_system_map,
    recommend_next_build,
)


router = APIRouter(prefix="/build-accelerator", tags=["Build Accelerator"])


class NextBuildRequest(BaseModel):
    focus: str = ""
    capacity: int = Field(3, ge=1, le=10)


class BuildSprintRequest(BaseModel):
    sprint_name: str = "Salus Build Sprint"
    focus: str = ""
    capacity: int = Field(3, ge=1, le=7)
    include_release_checklist: bool = True


class ReleaseChecklistRequest(BaseModel):
    changed_files: List[str] = Field(default_factory=list)


class SmokeTestPlanRequest(BaseModel):
    include_optional: bool = True


class CommitPackRequest(BaseModel):
    files: List[str] = Field(default_factory=list)
    message: str = "add build accelerator module"


@router.get("/framework")
def framework():
    return {
        "name": "Project Salus Build Accelerator & System Map V1",
        "purpose": "Speed up Project Salus builds by mapping modules, selecting next builds, planning sprints, and standardizing release checks.",
        "core_modules_tracked": len(CORE_MODULES),
        "next_build_candidates": [item["key"] for item in NEXT_BUILD_CANDIDATES],
        "outputs": [
            "system_map",
            "next_build",
            "build_sprint",
            "release_checklist",
            "smoke_test_plan",
            "commit_pack",
        ],
    }


@router.get("/system-map")
def system_map():
    return build_system_map()


@router.post("/next-build")
def next_build(request: NextBuildRequest):
    return recommend_next_build(
        request.model_dump() if hasattr(request, "model_dump") else request.dict()
    )


@router.post("/sprint")
def sprint(request: BuildSprintRequest):
    return build_sprint(
        request.model_dump() if hasattr(request, "model_dump") else request.dict()
    )


@router.post("/release-checklist")
def release_checklist(request: ReleaseChecklistRequest):
    return build_release_checklist(
        request.model_dump() if hasattr(request, "model_dump") else request.dict()
    )


@router.post("/smoke-test-plan")
def smoke_test_plan(request: SmokeTestPlanRequest):
    return build_smoke_test_plan(
        request.model_dump() if hasattr(request, "model_dump") else request.dict()
    )


@router.post("/commit-pack")
def commit_pack(request: CommitPackRequest):
    return build_commit_pack(
        request.model_dump() if hasattr(request, "model_dump") else request.dict()
    )
