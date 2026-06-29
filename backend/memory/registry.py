import importlib
from pathlib import Path
from typing import Any

from backend.agents import __path__ as agent_paths


def discover_agents() -> list[dict[str, Any]]:
    agents: list[dict[str, Any]] = []
    for module_path in Path(__file__).resolve().parent.parent.joinpath("agents").glob("*.py"):
        if module_path.name.startswith("_"):
            continue
        module_name = f"backend.agents.{module_path.stem}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        agent_payload = getattr(module, "AGENT", None)
        if isinstance(agent_payload, dict):
            agents.append({
                "name": agent_payload.get("name", module_path.stem.replace("_", " ").title()),
                "status": agent_payload.get("status", "active"),
                "mission": agent_payload.get("mission", ""),
                "module": module_name,
            })
        elif hasattr(agent_payload, "name"):
            agents.append({
                "name": getattr(agent_payload, "name", module_path.stem.replace("_", " ").title()),
                "status": getattr(agent_payload, "status", "active"),
                "mission": getattr(agent_payload, "mission", ""),
                "module": module_name,
            })
    return sorted(agents, key=lambda item: item["name"])
