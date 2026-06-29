import ast
from pathlib import Path


def is_valid_python_file(path: Path) -> bool:
    if not path.exists():
        return False

    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return False

    return True


def is_duplicate_directorate(project_root: Path, slug: str, title: str) -> bool:
    candidates = [
        project_root / "backend" / "api" / f"{slug}.py",
        project_root / "backend" / "services" / f"{slug}_service.py",
        project_root / "backend" / "agents" / f"{slug}_agent.py",
        project_root / "backend" / "directorates" / f"{slug}.py",
        project_root / "docs" / f"{slug}.md",
        project_root / "tests" / f"test_{slug}.py",
    ]
    if any(path.exists() for path in candidates):
        return True

    registry_path = project_root / "backend" / "directorates" / "registry.py"
    if registry_path.exists():
        registry_text = registry_path.read_text(encoding="utf-8")
        return title.lower() in registry_text.lower()

    return False
