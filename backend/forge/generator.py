import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.forge.registry import build_directorate_components
from backend.forge.validator import (
    is_duplicate_directorate,
    is_valid_python_file,
    validate_directorate_name,
    validate_directorate_structure,
)

BASE_DIR = Path(__file__).resolve().parents[2]


def slugify(name: str) -> str:
    return "_".join(part.lower() for part in re.split(r"[^a-zA-Z0-9]+", name) if part)


def titleize(name: str) -> str:
    parts = [part.capitalize() for part in re.split(r"[^a-zA-Z0-9]+", name) if part]
    return " ".join(parts)


def classify_name(slug: str) -> str:
    return "".join(part.capitalize() for part in slug.split("_") if part)


def _ensure_package_dirs(root: Path) -> None:
    for package_dir in [
        root / "backend" / "api",
        root / "backend" / "services",
        root / "backend" / "agents",
        root / "backend" / "directorates",
    ]:
        package_dir.mkdir(parents=True, exist_ok=True)
        init_file = package_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Generated package for Salus Forge."""\n', encoding="utf-8")


def _snapshot_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _restore_snapshot(path: Path, content: Optional[str]) -> None:
    if content is None:
        if path.exists():
            path.unlink()
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def register_directorate(root: Path, slug: str, title: str, class_name: str) -> Path:
    registry_path = root / "backend" / "directorates" / "registry.py"
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    import_line = f"from backend.directorates.{slug} import {class_name}Directorate\n"
    if not registry_path.exists():
        registry_path.write_text(
            "from backend.directorates.base import Directorate\n"
            f"{import_line}"
            "\nDIRECTORATES = {}\n",
            encoding="utf-8",
        )
        return registry_path

    registry_text = registry_path.read_text(encoding="utf-8")
    if f'"{title}"' in registry_text:
        return registry_path

    if import_line not in registry_text:
        registry_text = registry_text.replace(
            "from backend.directorates.base import Directorate\n",
            f"from backend.directorates.base import Directorate\n{import_line}",
            1,
        )

    if "DIRECTORATES = {" in registry_text:
        registry_text = re.sub(
            r"(\n\})\s*$",
            f'\n    "{title}": {class_name}Directorate,\n}}',
            registry_text.rstrip() + "\n",
            count=1,
        )
    else:
        registry_text = (
            "from backend.directorates.base import Directorate\n"
            f"{import_line}"
            f"\nDIRECTORATES = {{\n    \"{title}\": {class_name}Directorate,\n}}\n"
        )

    registry_path.write_text(registry_text, encoding="utf-8")
    return registry_path


def _update_api_router(root: Path, slug: str, title: str) -> None:
    router_path = root / "backend" / "api" / "routes.py"
    router_path.parent.mkdir(parents=True, exist_ok=True)
    if not router_path.exists():
        router_path.write_text("from fastapi import APIRouter\n\nrouter = APIRouter()\n", encoding="utf-8")

    router_text = router_path.read_text(encoding="utf-8")
    import_line = f"from backend.api.{slug} import router as {slug}_router\n"
    include_line = f"router.include_router({slug}_router)\n"
    if import_line not in router_text:
        router_text = router_text.replace(
            "from fastapi import APIRouter\n\n",
            f"from fastapi import APIRouter\n\n{import_line}\n",
            1,
        )
    if include_line not in router_text:
        router_text = router_text.rstrip() + f"\n\n{include_line}"
    router_path.write_text(router_text, encoding="utf-8")


def _update_navigation(root: Path, slug: str, title: str) -> None:
    nav_path = root / "frontend" / "navigation.json"
    nav_path.parent.mkdir(parents=True, exist_ok=True)
    if nav_path.exists():
        try:
            data = json.loads(nav_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {"directorates": []}
    else:
        data = {"directorates": []}

    directorates = data.get("directorates", []) if isinstance(data, dict) else []
    if not isinstance(directorates, list):
        directorates = []
    if not any(item.get("slug") == slug for item in directorates if isinstance(item, dict)):
        directorates.append({"name": title, "slug": slug, "path": f"/{slug}"})
    data = {"directorates": directorates}
    nav_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _update_docs_index(root: Path, slug: str, title: str) -> None:
    index_path = root / "docs" / "index.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
    else:
        content = "# Project Salus Documentation\n\n"
    bullet = f"- [{title}]({slug}/README.md)"
    if bullet not in content:
        content = content.rstrip() + "\n\n" + bullet + "\n"
    index_path.write_text(content, encoding="utf-8")


def _build_plugin_manifest(slug: str, title: str, class_name: str, dependencies: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "name": title,
        "slug": slug,
        "version": "1.0.0",
        "enabled": True,
        "dependencies": dependencies or [],
        "health": {"status": "healthy"},
        "class_name": f"{class_name}Directorate",
    }


def _read_plugin_manifest(plugin_path: Path) -> Dict[str, Any]:
    if plugin_path.exists():
        try:
            payload = json.loads(plugin_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
    else:
        payload = {}

    if not isinstance(payload, dict):
        payload = {}

    slug = plugin_path.parent.name
    title = slug.replace("_", " ").title()
    payload.setdefault("name", title)
    payload.setdefault("slug", slug)
    payload.setdefault("version", "1.0.0")
    payload.setdefault("enabled", True)
    payload.setdefault("dependencies", [])
    payload.setdefault("health", {"status": "healthy"})
    if not isinstance(payload.get("dependencies"), list):
        payload["dependencies"] = []
    if not isinstance(payload.get("health"), dict):
        payload["health"] = {"status": "healthy"}
    return payload


def _write_plugin_metadata(root: Path, slug: str, title: str, class_name: str, dependencies: Optional[List[str]] = None) -> None:
    plugin_dir = root / "backend" / "directorates" / slug
    plugin_dir.mkdir(parents=True, exist_ok=True)
    plugin_config = _build_plugin_manifest(slug, title, class_name, dependencies=dependencies)
    (plugin_dir / "plugin.json").write_text(json.dumps(plugin_config, indent=2), encoding="utf-8")


def _get_plugin_health(plugin_dir: Path, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    defaults = {"status": "healthy"}
    if payload and isinstance(payload.get("health"), dict):
        defaults.update(payload["health"])
    required_files = [plugin_dir / "__init__.py", plugin_dir / "plugin.json", plugin_dir / "manifest.json"]
    missing = [path.name for path in required_files if not path.exists()]
    if missing:
        defaults["status"] = "degraded"
        defaults["missing"] = missing
    return defaults


def _append_log(root: Path, directorate: str, files_created: List[str], execution_time: float, success: bool) -> None:
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "forge.log"
    timestamp = datetime.now(timezone.utc).isoformat()
    status = "success" if success else "failure"
    line = (
        f"timestamp={timestamp} directorate={directorate} files_created={','.join(files_created) or '-'} "
        f"execution_time={execution_time:.3f}s success={status}\n"
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def rollback_directorate(name: str, project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or BASE_DIR).resolve()
    slug = slugify(name)
    title = titleize(name)
    class_name = classify_name(slug)

    created_paths = [
        root / "backend" / "api" / f"{slug}.py",
        root / "backend" / "services" / f"{slug}_service.py",
        root / "backend" / "agents" / f"{slug}_agent.py",
        root / "backend" / "directorates" / slug,
        root / "docs" / slug,
        root / "tests" / slug,
    ]
    for path in created_paths:
        if path.is_dir():
            for child in sorted(path.rglob("*"), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            if path.exists():
                path.rmdir()
        elif path.exists():
            path.unlink()

    registry_path = root / "backend" / "directorates" / "registry.py"
    if registry_path.exists():
        text = registry_path.read_text(encoding="utf-8")
        text = text.replace(f"from backend.directorates.{slug} import {class_name}Directorate\n", "")
        text = text.replace(f'\n    "{title}": {class_name}Directorate,', "")
        registry_path.write_text(text, encoding="utf-8")

    router_path = root / "backend" / "api" / "routes.py"
    if router_path.exists():
        text = router_path.read_text(encoding="utf-8")
        text = text.replace(f"from backend.api.{slug} import router as {slug}_router\n", "")
        text = text.replace(f"router.include_router({slug}_router)\n", "")
        router_path.write_text(text, encoding="utf-8")

    nav_path = root / "frontend" / "navigation.json"
    if nav_path.exists():
        try:
            data = json.loads(nav_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                items = [item for item in data.get("directorates", []) if isinstance(item, dict) and item.get("slug") != slug]
                data["directorates"] = items
                nav_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except json.JSONDecodeError:
            pass

    index_path = root / "docs" / "index.md"
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        bullet = f"- [{title}]({slug}/README.md)"
        if bullet in content:
            content = content.replace(bullet, "")
            index_path.write_text(content.replace("\n\n\n", "\n\n"), encoding="utf-8")

    _append_log(root, title, [], 0.0, False)
    return {"directorate": title, "slug": slug, "rolled_back": True}


def discover_plugins(project_root: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    root = Path(project_root or BASE_DIR).resolve()
    plugins: List[Dict[str, Any]] = []
    directorates_dir = root / "backend" / "directorates"
    if not directorates_dir.exists():
        return plugins

    for child in sorted(directorates_dir.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "__init__.py").exists() and not (child / "plugin.json").exists():
            continue
        payload = _read_plugin_manifest(child / "plugin.json")
        health = _get_plugin_health(child, payload)
        plugins.append({
            "name": payload.get("name", child.name.replace("_", " ").title()),
            "slug": payload.get("slug", child.name),
            "version": payload.get("version", "1.0.0"),
            "enabled": bool(payload.get("enabled", True)),
            "dependencies": payload.get("dependencies", []),
            "health": health,
            "path": str(child.relative_to(root)),
        })
    return plugins


def enable_plugin(plugin_slug: str, project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or BASE_DIR).resolve()
    plugin_dir = root / "backend" / "directorates" / plugin_slug
    plugin_path = plugin_dir / "plugin.json"
    if not plugin_dir.exists() or not plugin_dir.is_dir():
        raise ValueError(f"Plugin '{plugin_slug}' not found")
    payload = _read_plugin_manifest(plugin_path)
    payload["enabled"] = True
    plugin_path.parent.mkdir(parents=True, exist_ok=True)
    plugin_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"slug": plugin_slug, "enabled": True}


def disable_plugin(plugin_slug: str, project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or BASE_DIR).resolve()
    plugin_dir = root / "backend" / "directorates" / plugin_slug
    plugin_path = plugin_dir / "plugin.json"
    if not plugin_dir.exists() or not plugin_dir.is_dir():
        raise ValueError(f"Plugin '{plugin_slug}' not found")
    payload = _read_plugin_manifest(plugin_path)
    payload["enabled"] = False
    plugin_path.parent.mkdir(parents=True, exist_ok=True)
    plugin_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"slug": plugin_slug, "enabled": False}


def create_directorate(name: str, project_root: Optional[Path | str] = None, overwrite: bool = False) -> Dict[str, Any]:
    if not validate_directorate_name(name):
        raise ValueError("Directorate name is invalid")

    root = Path(project_root or BASE_DIR).resolve()
    root.mkdir(parents=True, exist_ok=True)

    slug = slugify(name)
    title = titleize(name)
    class_name = classify_name(slug)

    if is_duplicate_directorate(root, slug, title) and not overwrite:
        raise ValueError(f"Directorate '{title}' already exists")

    components = build_directorate_components(slug=slug, title=title, class_name=class_name)

    created: List[str] = []
    skipped: List[str] = []
    validated: List[str] = []

    _ensure_package_dirs(root)

    snapshots = {
        str(root / "backend" / "directorates" / "registry.py"): _snapshot_file(root / "backend" / "directorates" / "registry.py"),
        str(root / "backend" / "api" / "routes.py"): _snapshot_file(root / "backend" / "api" / "routes.py"),
        str(root / "frontend" / "navigation.json"): _snapshot_file(root / "frontend" / "navigation.json"),
        str(root / "docs" / "index.md"): _snapshot_file(root / "docs" / "index.md"),
    }

    started = time.perf_counter()
    try:
        for component in components:
            destination = root / component.relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)

            template = component.template
            content = template.format(slug=slug, title=title, class_name=class_name)

            if destination.exists() and not overwrite and destination.suffix == ".py" and is_valid_python_file(destination):
                skipped.append(str(destination.relative_to(root)))
                continue

            if destination.exists() and not overwrite and destination.suffix != ".py" and destination.stat().st_size > 0:
                skipped.append(str(destination.relative_to(root)))
                continue

            destination.write_text(content, encoding="utf-8")
            created.append(str(destination.relative_to(root)))

        register_directorate(root, slug, title, class_name)
        _write_plugin_metadata(root, slug, title, class_name)
        _update_api_router(root, slug, title)
        _update_navigation(root, slug, title)
        _update_docs_index(root, slug, title)
        validated.extend(validate_directorate_structure(root, slug, title))
        _append_log(root, title, created, time.perf_counter() - started, True)
        return {
            "directorate": title,
            "slug": slug,
            "created": created,
            "skipped_existing": skipped,
            "validated": validated,
            "project_root": str(root),
        }
    except Exception as exc:
        for path, content in snapshots.items():
            _restore_snapshot(Path(path), content)
        for path in created:
            candidate = root / path
            if candidate.exists():
                if candidate.is_dir():
                    for child in sorted(candidate.rglob("*"), reverse=True):
                        if child.is_file() or child.is_symlink():
                            child.unlink()
                        elif child.is_dir():
                            child.rmdir()
                    if candidate.exists():
                        candidate.rmdir()
                else:
                    candidate.unlink()
        _append_log(root, title, created, time.perf_counter() - started, False)
        raise RuntimeError(f"Forge generation failed for '{title}': {exc}") from exc
