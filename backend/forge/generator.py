import re
from pathlib import Path
from typing import Dict, List, Optional

from backend.forge.registry import build_directorate_components
from backend.forge.validator import is_duplicate_directorate, is_valid_python_file

BASE_DIR = Path(__file__).resolve().parents[2]


def slugify(name: str) -> str:
    return "_".join(part.lower() for part in name.replace("-", " ").split() if part)


def titleize(name: str) -> str:
    return " ".join(part.capitalize() for part in name.replace("-", " ").replace("_", " ").split() if part)


def classify_name(slug: str) -> str:
    return "".join(part.capitalize() for part in slug.split("_") if part)


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


def create_directorate(name: str, project_root: Optional[Path | str] = None, overwrite: bool = False) -> Dict[str, object]:
    root = Path(project_root or BASE_DIR).resolve()
    root.mkdir(parents=True, exist_ok=True)

    slug = slugify(name)
    title = titleize(name)
    class_name = classify_name(slug)

    if is_duplicate_directorate(root, slug, title):
        raise ValueError(f"Directorate '{title}' already exists")

    components = build_directorate_components(slug=slug, title=title, class_name=class_name)

    created: List[str] = []
    skipped: List[str] = []
    validated: List[str] = []

    package_dirs = [
        root / "backend" / "api",
        root / "backend" / "services",
        root / "backend" / "agents",
        root / "backend" / "directorates",
    ]
    for package_dir in package_dirs:
        package_dir.mkdir(parents=True, exist_ok=True)
        init_file = package_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("\"\"\"Generated package for Salus Forge.\"\"\"\n", encoding="utf-8")

    registry_path = register_directorate(root, slug, title, class_name)

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

        if destination.suffix == ".py" and is_valid_python_file(destination):
            validated.append(str(destination.relative_to(root)))

    if registry_path.exists():
        validated.append(str(registry_path.relative_to(root)))

    return {
        "directorate": title,
        "slug": slug,
        "created": created,
        "skipped_existing": skipped,
        "validated": validated,
        "project_root": str(root),
    }
