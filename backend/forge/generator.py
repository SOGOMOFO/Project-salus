from pathlib import Path
from backend.forge.templates import (
    API_TEMPLATE,
    SERVICE_TEMPLATE,
    AGENT_TEMPLATE,
    DOC_TEMPLATE,
    TEST_TEMPLATE,
)

BASE_DIR = Path(__file__).resolve().parents[2]

def slugify(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")

def titleize(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").title()

def create_directorate(name: str):
    slug = slugify(name)
    title = titleize(name)

    files = {
        BASE_DIR / "backend" / "api" / f"{slug}.py": API_TEMPLATE.format(slug=slug, title=title),
        BASE_DIR / "backend" / "services" / f"{slug}_service.py": SERVICE_TEMPLATE.format(slug=slug, title=title),
        BASE_DIR / "backend" / "agents" / f"{slug}_agent.py": AGENT_TEMPLATE.format(slug=slug, title=title),
        BASE_DIR / "docs" / f"{slug}.md": DOC_TEMPLATE.format(slug=slug, title=title),
        BASE_DIR / "tests" / f"test_{slug}.py": TEST_TEMPLATE.format(slug=slug, title=title),
    }

    created = []
    skipped = []

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            skipped.append(str(path.relative_to(BASE_DIR)))
        else:
            path.write_text(content)
            created.append(str(path.relative_to(BASE_DIR)))

    return {
        "directorate": title,
        "slug": slug,
        "created": created,
        "skipped_existing": skipped,
    }
