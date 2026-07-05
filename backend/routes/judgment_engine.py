from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from backend.services.judgment_engine_service import (
    create_judgment_item,
    get_judgment_item,
    judgment_status,
    list_judgment_items,
    score_judgment,
)


router = APIRouter(tags=["judgment-engine"])


@router.get("/api/judgment-engine/status")
async def judgment_engine_status_api() -> dict[str, Any]:
    return judgment_status()


@router.post("/api/judgment-engine/score")
async def score_judgment_api(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "score": score_judgment(payload),
    }


@router.post("/api/judgment-engine/item")
async def create_judgment_item_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        item = create_judgment_item(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "item": item,
    }


@router.get("/api/judgment-engine/items")
async def list_judgment_items_api(
    query: str | None = Query(default=None),
    recommendation: str | None = Query(default=None),
) -> dict[str, Any]:
    items = list_judgment_items(query=query, recommendation=recommendation)

    return {
        "status": "ok",
        "count": len(items),
        "items": items,
    }


@router.get("/api/judgment-engine/item/{item_id}")
async def get_judgment_item_api(item_id: str) -> dict[str, Any]:
    item = get_judgment_item(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="judgment item not found")

    return {
        "status": "ok",
        "item": item,
    }


@router.get("/command/judgment", response_class=HTMLResponse)
async def judgment_page() -> HTMLResponse:
    return HTMLResponse(
        content="""
        <!doctype html>
        <html>
          <head>
            <title>Project Salus — Judgment Engine</title>
          </head>
          <body>
            <h1>Project Salus — Judgment Engine</h1>
            <p>Track decisions, evidence, risks, confidence, recommendations, and next actions.</p>

            <h2>Navigation</h2>
            <a href="/command/knowledge">Knowledge</a>
            <a href="/command/memory">Memory</a>
            <a href="/command/navigation">Navigation</a>
            <a href="/command/workflows">Workflows</a>

            <h2>Status</h2>
            <pre id="status">Loading...</pre>

            <h2>Judgment Items</h2>
            <pre id="items">Loading...</pre>

            <script>
              fetch("/api/judgment-engine/status")
                .then(response => response.json())
                .then(data => {
                  document.getElementById("status").textContent = JSON.stringify(data, null, 2);
                });

              fetch("/api/judgment-engine/items")
                .then(response => response.json())
                .then(data => {
                  document.getElementById("items").textContent = JSON.stringify(data, null, 2);
                });
            </script>
          </body>
        </html>
        """
    )
