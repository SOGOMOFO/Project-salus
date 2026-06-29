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
            name="package_init",
            template=forge_templates.DIRECTORATE_PACKAGE_INIT_TEMPLATE,
            relative_path=f"backend/directorates/{slug}/__init__.py",
        ),
        DirectorateComponent(
            name="directorate_agent",
            template=forge_templates.DIRECTORATE_AGENT_TEMPLATE,
            relative_path=f"backend/directorates/{slug}/agent.py",
        ),
        DirectorateComponent(
            name="directorate_service",
            template=forge_templates.DIRECTORATE_SERVICE_TEMPLATE,
            relative_path=f"backend/directorates/{slug}/service.py",
        ),
        DirectorateComponent(
            name="directorate_api",
            template=forge_templates.DIRECTORATE_API_TEMPLATE,
            relative_path=f"backend/directorates/{slug}/api.py",
        ),
        DirectorateComponent(
            name="directorate_models",
            template=forge_templates.DIRECTORATE_MODELS_TEMPLATE,
            relative_path=f"backend/directorates/{slug}/models.py",
        ),
        DirectorateComponent(
            name="directorate_memory",
            template=forge_templates.DIRECTORATE_MEMORY_TEMPLATE,
            relative_path=f"backend/directorates/{slug}/memory.py",
        ),
        DirectorateComponent(
            name="directorate_prompts",
            template=forge_templates.DIRECTORATE_PROMPTS_TEMPLATE,
            relative_path=f"backend/directorates/{slug}/prompts.py",
        ),
        DirectorateComponent(
            name="directorate_manifest",
            template=forge_templates.DIRECTORATE_MANIFEST_TEMPLATE,
            relative_path=f"backend/directorates/{slug}/manifest.json",
        ),
        DirectorateComponent(
            name="docs",
            template=forge_templates.DIRECTORATE_DOC_TEMPLATE,
            relative_path=f"docs/{slug}/README.md",
        ),
        DirectorateComponent(
            name="tests",
            template=forge_templates.DIRECTORATE_TEST_TEMPLATE,
            relative_path=f"tests/{slug}/test_{slug}.py",
        ),
    ]
