from dataclasses import dataclass
from typing import List

from backend.forge import templates as forge_templates


@dataclass(frozen=True)
class DirectorateComponent:
    name: str
    template: str
    relative_path: str


def build_directorate_components(slug: str, title: str, class_name: str) -> List[DirectorateComponent]:
    return [
        DirectorateComponent(
            name="api",
            template=forge_templates.API_TEMPLATE,
            relative_path=f"backend/api/{slug}.py",
        ),
        DirectorateComponent(
            name="service",
            template=forge_templates.SERVICE_TEMPLATE,
            relative_path=f"backend/services/{slug}_service.py",
        ),
        DirectorateComponent(
            name="agent",
            template=forge_templates.AGENT_TEMPLATE,
            relative_path=f"backend/agents/{slug}_agent.py",
        ),
        DirectorateComponent(
            name="docs",
            template=forge_templates.DOC_TEMPLATE,
            relative_path=f"docs/{slug}.md",
        ),
        DirectorateComponent(
            name="tests",
            template=forge_templates.TEST_TEMPLATE,
            relative_path=f"tests/test_{slug}.py",
        ),
    ]
