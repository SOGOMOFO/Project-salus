from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def route_source_paths(source_path: str | Path = "backend/main.py") -> list[Path]:
    primary = Path(source_path)
    paths = [primary]

    if primary.name == "main.py":
        routes_dir = Path("backend/routes")
        if routes_dir.exists():
            paths.extend(sorted(path for path in routes_dir.glob("*.py") if path.name != "__init__.py"))

    return paths


def _decorator_to_route(decorator: ast.AST, source_file: str) -> dict[str, Any] | None:
    if not isinstance(decorator, ast.Call):
        return None

    func = decorator.func

    if not isinstance(func, ast.Attribute):
        return None

    if not isinstance(func.value, ast.Name):
        return None

    if func.value.id not in {"app", "router"}:
        return None

    if func.attr not in HTTP_METHODS:
        return None

    path = None

    if decorator.args and isinstance(decorator.args[0], ast.Constant):
        path = decorator.args[0].value

    return {
        "method": func.attr.upper(),
        "path": path,
        "source_file": source_file,
        "decorator_owner": func.value.id,
    }


def _collect_routes_single(source_path: Path) -> list[dict[str, Any]]:
    source = source_path.read_text()
    tree = ast.parse(source)

    routes: list[dict[str, Any]] = []

    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for decorator in node.decorator_list:
            route = _decorator_to_route(decorator, str(source_path))
            if route:
                route["handler"] = node.name
                routes.append(route)

    return routes


def collect_routes(source_path: str | Path = "backend/main.py") -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []

    for path in route_source_paths(source_path):
        if path.exists():
            routes.extend(_collect_routes_single(path))

    return sorted(
        routes,
        key=lambda item: (
            str(item.get("path") or ""),
            str(item.get("method") or ""),
            str(item.get("handler") or ""),
            str(item.get("source_file") or ""),
        ),
    )


def collect_sprint_markers(source_path: str | Path = "backend/main.py") -> list[str]:
    path = Path(source_path)
    markers: list[str] = []

    if not path.exists():
        return markers

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("# --- Sprint"):
            markers.append(stripped.strip("# ").strip())

    return markers


def collect_file_metrics(source_path: str | Path = "backend/main.py") -> dict[str, Any]:
    path = Path(source_path)
    text = path.read_text()
    routes = collect_routes(path)

    return {
        "path": str(path),
        "line_count": len(text.splitlines()),
        "character_count": len(text),
        "sprint_marker_count": len(collect_sprint_markers(path)),
        "route_count": len(routes),
        "route_source_count": len(route_source_paths(path)),
    }


def build_inventory(source_path: str | Path = "backend/main.py") -> dict[str, Any]:
    routes = collect_routes(source_path)
    markers = collect_sprint_markers(source_path)
    metrics = collect_file_metrics(source_path)

    return {
        "status": "ok",
        "module": "local_mvp_hardening_audit",
        "source": str(source_path),
        "metrics": metrics,
        "sprint_markers": markers,
        "routes": routes,
        "route_count": len(routes),
        "sprint_marker_count": len(markers),
        "recommendation": "Continue modular route extraction one route group at a time with tests green after every extraction.",
    }


def to_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# Project Salus Route Inventory",
        "",
        "## Summary",
        f"- Source: `{inventory['source']}`",
        f"- Route count: {inventory['route_count']}",
        f"- Sprint marker count: {inventory['sprint_marker_count']}",
        f"- Line count: {inventory['metrics']['line_count']}",
        f"- Route source count: {inventory['metrics'].get('route_source_count')}",
        "",
        "## Sprint Markers",
    ]

    for marker in inventory["sprint_markers"]:
        lines.append(f"- {marker}")

    lines.extend([
        "",
        "## Routes",
        "",
        "| Method | Path | Handler | Source | Owner |",
        "|---|---|---|---|---|",
    ])

    for route in inventory["routes"]:
        lines.append(
            f"| {route.get('method')} | `{route.get('path')}` | `{route.get('handler')}` | `{route.get('source_file')}` | `{route.get('decorator_owner')}` |"
        )

    lines.extend([
        "",
        "## Recommendation",
        inventory["recommendation"],
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    inventory = build_inventory()
    print(json.dumps(inventory, indent=2))


if __name__ == "__main__":
    main()
