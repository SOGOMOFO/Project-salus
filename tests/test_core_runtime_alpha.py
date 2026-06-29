import asyncio
import unittest

from backend.core.commander_api import create_commander_router
from backend.core.event_bus import EventBus
from backend.core.health_monitor import HealthMonitor
from backend.core.mission_planner import MissionPlanner
from backend.core.agent_runtime import AgentRuntime
from backend.memory.service import MemoryEngine


class CoreRuntimeAlphaTests(unittest.TestCase):
    def test_event_bus_publish_history_metrics(self):
        bus = EventBus()
        seen = []
        bus.subscribe("mission.created", lambda payload: seen.append(payload.get("id")))

        event = bus.publish("mission.created", {"id": 42})
        self.assertEqual(event["topic"], "mission.created")
        self.assertEqual(seen, [42])

        history = bus.history("mission.created")
        self.assertEqual(len(history), 1)
        metrics = bus.metrics()
        self.assertEqual(metrics["published_events"], 1)
        self.assertEqual(metrics["topics"]["mission.created"], 1)

    def test_health_monitor_summary(self):
        monitor = HealthMonitor(name="salus")
        monitor.record_check("api", "ok", "alive")
        monitor.record_check("plugins", "degraded", "missing manifest")
        summary = monitor.summary()
        self.assertEqual(summary["status"], "degraded")
        self.assertIn("plugins", summary["unhealthy_components"])

    def test_commander_router_exposes_core_health_and_events(self):
        runtime = AgentRuntime()
        runtime.bootstrap_default_agents()
        planner = MissionPlanner()
        planner.initialize()
        memory_engine = MemoryEngine()
        memory_engine.initialize()
        bus = EventBus()
        monitor = HealthMonitor()

        def verifier(value):
            if value != "salus-secure":
                raise ValueError("unauthorized")

        router = create_commander_router(
            agent_runtime=runtime,
            mission_planner=planner,
            memory_engine=memory_engine,
            event_bus=bus,
            health_monitor=monitor,
            verify_passphrase=verifier,
            version="0.4.0",
        )
        core_index = next(route.endpoint for route in router.routes if route.path == "/core" and "GET" in route.methods)
        core_events = next(route.endpoint for route in router.routes if route.path == "/core/events" and "GET" in route.methods)
        core_health = next(route.endpoint for route in router.routes if route.path == "/core/health" and "GET" in route.methods)

        index_payload = asyncio.run(core_index())
        self.assertEqual(index_payload["status"], "ok")
        self.assertIn("/core/health", index_payload["routes"])

        bus.publish("agent.run", {"name": "x"})
        events_payload = asyncio.run(core_events("salus-secure", None, 10))
        self.assertEqual(events_payload["status"], "ok")
        self.assertGreaterEqual(events_payload["metrics"]["published_events"], 1)

        health_payload = asyncio.run(core_health("salus-secure"))
        self.assertIn("status", health_payload)
        self.assertIn("checks", health_payload)


if __name__ == "__main__":
    unittest.main()
