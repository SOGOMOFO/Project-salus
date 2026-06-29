import ast
import json
import re
from pathlib import Path
from typing import List


_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _-]*$")


def is_valid_python_file(path: Path) -> bool:
    if not path.exists():
        return False

    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return False

    return True


def validate_directorate_name(name: str) -> bool:
    return bool(name and _NAME_PATTERN.fullmatch(name))


def is_duplicate_directorate(project_root: Path, slug: str, title: str) -> bool:
    candidates = [
        project_root / "backend" / "api" / f"{slug}.py",
        project_root / "backend" / "services" / f"{slug}_service.py",
        project_root / "backend" / "agents" / f"{slug}_agent.py",
        project_root / "backend" / "directorates" / slug / "__init__.py",
        project_root / "docs" / slug / "README.md",
        project_root / "tests" / slug / f"test_{slug}.py",
    ]
    if any(path.exists() for path in candidates):
        return True

    registry_path = project_root / "backend" / "directorates" / "registry.py"
    if registry_path.exists():
        registry_text = registry_path.read_text(encoding="utf-8")
        return title.lower() in registry_text.lower()

    return False


def validate_directorate_structure(project_root: Path, slug: str, title: str) -> List[str]:
    expected_paths = [
        project_root / "backend" / "api" / f"{slug}.py",
        project_root / "backend" / "services" / f"{slug}_service.py",
        project_root / "backend" / "agents" / f"{slug}_agent.py",
        project_root / "backend" / "directorates" / slug / "__init__.py",
        project_root / "backend" / "directorates" / slug / "agent.py",
        project_root / "backend" / "directorates" / slug / "service.py",
        project_root / "backend" / "directorates" / slug / "api.py",
        project_root / "backend" / "directorates" / slug / "models.py",
        project_root / "backend" / "directorates" / slug / "memory.py",
        project_root / "backend" / "directorates" / slug / "prompts.py",
        project_root / "backend" / "directorates" / slug / "manifest.json",
        project_root / "backend" / "directorates" / slug / "plugin.json",
        project_root / "docs" / slug / "README.md",
        project_root / "tests" / slug / f"test_{slug}.py",
    ]
    missing = [str(path.relative_to(project_root)) for path in expected_paths if not path.exists()]
    if missing:
        raise ValueError(f"Missing directorate files for '{title}': {', '.join(missing)}")

    for path in expected_paths:
        if path.suffix == ".py" and not is_valid_python_file(path):
            raise ValueError(f"Invalid Python syntax in {path.relative_to(project_root)}")
        if path.name == "plugin.json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid plugin configuration in {path.relative_to(project_root)}") from exc

    return [str(path.relative_to(project_root)) for path in expected_paths]
