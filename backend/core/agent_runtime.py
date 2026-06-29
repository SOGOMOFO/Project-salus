from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from backend.memory.memory_engine import add_memory, initialize_memory_store
from backend.memory.registry import discover_agents


AgentHandler = Callable[[dict[str, Any]], tuple[str, float] | str]


@dataclass
class RegisteredAgent:
    name: str
    mission: str
    status: str
    handler: AgentHandler


class AgentRuntime:
    def __init__(self) -> None:
        self._registry: dict[str, RegisteredAgent] = {}

    def register_agent(
        self,
        *,
        name: str,
        mission: str,
        status: str = "active",
        handler: AgentHandler | None = None,
    ) -> dict[str, Any]:
        normalized_name = str(name or "").strip()
        if not normalized_name:
            raise ValueError("agent name is required")

        runtime_handler = handler or self._default_handler_for(normalized_name, mission)
        agent = RegisteredAgent(
            name=normalized_name,
            mission=str(mission or "").strip(),
            status=str(status or "active").strip() or "active",
            handler=runtime_handler,
        )
        self._registry[normalized_name.lower()] = agent
        return {"name": agent.name, "mission": agent.mission, "status": agent.status}

    def list_agents(self) -> list[dict[str, Any]]:
        agents = [
            {
                "name": agent.name,
                "mission": agent.mission,
                "status": agent.status,
            }
            for agent in self._registry.values()
        ]
        return sorted(agents, key=lambda item: item["name"])

    def run_agent(
        self,
        name: str,
        payload: dict[str, Any] | None = None,
        *,
        important: bool = False,
    ) -> dict[str, Any]:
        requested_name = str(name or "").strip()
        agent = self._registry.get(requested_name.lower())
        timestamp = datetime.now(timezone.utc).isoformat()
        input_payload = payload or {}

        if not agent:
            return {
                "status": "not_found",
                "agent": requested_name,
                "input": input_payload,
                "output": f"Agent '{requested_name}' is not registered.",
                "confidence": 0.0,
                "timestamp": timestamp,
            }

        run_output = agent.handler(input_payload)
        if isinstance(run_output, tuple):
            output, confidence = run_output
        else:
            output, confidence = run_output, 0.7

        result = {
            "status": "ok",
            "agent": agent.name,
            "input": input_payload,
            "output": str(output),
            "confidence": round(float(confidence), 2),
            "timestamp": timestamp,
        }

        should_store = important or result["confidence"] >= 0.85
        if should_store:
            try:
                initialize_memory_store()
                add_memory(
                    memory_type="agent",
                    title=f"Agent run: {agent.name}",
                    content=json.dumps(result, sort_keys=True),
                    tags=["agent-runtime", "important-output"],
                    source=agent.name,
                )
            except Exception:
                pass

        return result

    def bootstrap_default_agents(self) -> None:
        if self._registry:
            return

        for discovered in discover_agents():
            self.register_agent(
                name=discovered.get("name", "Unknown Agent"),
                mission=discovered.get("mission", ""),
                status=discovered.get("status", "active"),
            )

    @staticmethod
    def _default_handler_for(name: str, mission: str) -> AgentHandler:
        def _handler(payload: dict[str, Any]) -> tuple[str, float]:
            objective = str(payload.get("objective", "")).strip()
            context = str(payload.get("context", "")).strip()
            prompt_bits = [part for part in [objective, context] if part]
            prompt = " | ".join(prompt_bits) if prompt_bits else "No specific objective provided."
            output = (
                f"{name} analyzed objective: {prompt}. "
                f"Mission alignment: {mission or 'No mission provided.'}"
            )
            confidence = 0.9 if objective else 0.82
            return output, confidence

        return _handler
