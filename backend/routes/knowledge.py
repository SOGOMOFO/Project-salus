from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from backend.services.knowledge_service import (
    create_knowledge_item,
    get_knowledge_item,
    knowledge_status,
    list_knowledge_items,
)


router = APIRouter(tags=["knowledge-engine"])


@router.get("/api/knowledge/status")
async def knowledge_status_api() -> dict[str, Any]:
    return knowledge_status()


@router.post("/api/knowledge/item")
async def create_knowledge_item_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        item = create_knowledge_item(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "item": item,
    }


@router.get("/api/knowledge/items")
async def list_knowledge_items_api(
    domain: str | None = Query(default=None),
    query: str | None = Query(default=None),
    tag: str | None = Query(default=None),
) -> dict[str, Any]:
    items = list_knowledge_items(domain=domain, query=query, tag=tag)

    return {
        "status": "ok",
        "count": len(items),
        "items": items,
    }


@router.get("/api/knowledge/item/{item_id}")
async def get_knowledge_item_api(item_id: str) -> dict[str, Any]:
    item = get_knowledge_item(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="knowledge item not found")

    return {
        "status": "ok",
        "item": item,
    }


@router.get("/command/knowledge", response_class=HTMLResponse)
async def knowledge_page() -> HTMLResponse:
    return HTMLResponse(
        content="""
        <!doctype html>
        <html>
          <head>
            <title>Project Salus — Knowledge Engine</title>
          </head>
          <body>
            <h1>Project Salus — Knowledge Engine</h1>
            <p>Capture, organize, and retrieve knowledge that improves judgment.</p>

            <h2>Navigation</h2>
            <a href="/command/navigation">Navigation</a>
            <a href="/command/workflows">Workflows</a>
            <a href="/command/daily-driver">Daily Driver</a>
            <a href="/command/records">Records</a>

            <h2>Status</h2>
            <pre id="status">Loading...</pre>

            <h2>Items</h2>
            <pre id="items">Loading...</pre>

            <script>
              fetch("/api/knowledge/status")
                .then(response => response.json())
                .then(data => {
                  document.getElementById("status").textContent = JSON.stringify(data, null, 2);
                });

              fetch("/api/knowledge/items")
                .then(response => response.json())
                .then(data => {
                  document.getElementById("items").textContent = JSON.stringify(data, null, 2);
                });
            </script>
          </body>
        </html>
        """
    )
