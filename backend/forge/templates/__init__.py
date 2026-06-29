import importlib.util
from pathlib import Path

_TEMPLATE_MODULE_PATH = Path(__file__).resolve().parent.parent / "templates.py"
_SPEC = importlib.util.spec_from_file_location("backend.forge.templates_module", _TEMPLATE_MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load forge templates from {_TEMPLATE_MODULE_PATH}")

_module = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_module)

API_TEMPLATE = _module.API_TEMPLATE
SERVICE_TEMPLATE = _module.SERVICE_TEMPLATE
AGENT_TEMPLATE = _module.AGENT_TEMPLATE
DOC_TEMPLATE = _module.DOC_TEMPLATE
TEST_TEMPLATE = _module.TEST_TEMPLATE

__all__ = [
    "API_TEMPLATE",
    "SERVICE_TEMPLATE",
    "AGENT_TEMPLATE",
    "DOC_TEMPLATE",
    "TEST_TEMPLATE",
]
