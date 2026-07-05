from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from backend.services.salus_memory_service import (
    create_memory_item,
    get_memory_item,
    list_memory_items,
    memory_status,
)


router = APIRouter(tags=["memory-engine"])


@router.get("/api/memory/status")
async def memory_status_api() -> dict[str, Any]:
    return memory_status()


@router.post("/api/memory/item")
async def create_memory_item_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        item = create_memory_item(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "item": item,
    }


@router.get("/api/memory/items")
async def list_memory_items_api(
    memory_type: str | None = Query(default=None),
    domain: str | None = Query(default=None),
    query: str | None = Query(default=None),
    tag: str | None = Query(default=None),
) -> dict[str, Any]:
    items = list_memory_items(
        memory_type=memory_type,
        domain=domain,
        query=query,
        tag=tag,
    )

    return {
        "status": "ok",
        "count": len(items),
        "items": items,
    }


@router.get("/api/memory/item/{item_id}")
async def get_memory_item_api(item_id: str) -> dict[str, Any]:
    item = get_memory_item(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="memory item not found")

    return {
        "status": "ok",
        "item": item,
    }


@router.get("/command/memory", response_class=HTMLResponse)
async def memory_page() -> HTMLResponse:
    return HTMLResponse(
        content="""
        <!doctype html>
        <html>
          <head>
            <title>Project Salus — Memory Engine</title>
          </head>
          <body>
            <h1>Project Salus — Memory Engine</h1>
            <p>Store working, long-term, mission, user, and knowledge memory.</p>

            <h2>Navigation</h2>
            <a href="/command/knowledge">Knowledge</a>
            <a href="/command/navigation">Navigation</a>
            <a href="/command/workflows">Workflows</a>
            <a href="/command/daily-driver">Daily Driver</a>

            <h2>Status</h2>
            <pre id="status">Loading...</pre>

            <h2>Memory Items</h2>
            <pre id="items">Loading...</pre>

            <script>
              fetch("/api/memory/status")
                .then(response => response.json())
                .then(data => {
                  document.getElementById("status").textContent = JSON.stringify(data, null, 2);
                });

              fetch("/api/memory/items")
                .then(response => response.json())
                .then(data => {
                  document.getElementById("items").textContent = JSON.stringify(data, null, 2);
                });
            </script>
          </body>
        </html>
        """
    )
