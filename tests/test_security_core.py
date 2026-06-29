import asyncio
import unittest

from fastapi import HTTPException

from backend.security.core import SecurityCore
from backend.security.api import security_status, security_audit, security_lockdown, security_unlock
from backend.security.security_core import security_core


class DummyRequest:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload


class SecurityCoreTests(unittest.TestCase):
    def test_security_core_module_path_exports_singleton(self):
        self.assertIsNotNone(security_core)

    def test_passphrase_compatibility_and_roles(self):
        core = SecurityCore()
        ctx = core.authorize(
            action="test.read",
            x_salus_passphrase="salus-secure",
            x_salus_role="readonly",
            allowed_roles={"readonly", "commander"},
        )
        self.assertEqual(ctx.role, "readonly")
        self.assertEqual(ctx.via, "passphrase")

    def test_invalid_credentials_denied(self):
        core = SecurityCore()
        with self.assertRaises(HTTPException):
            core.authorize(
                action="test.read",
                x_salus_passphrase="wrong",
                x_salus_token=None,
                x_salus_role="readonly",
            )

    def test_lockdown_blocks_non_commander(self):
        core = SecurityCore()
        core.set_lockdown(True)
        with self.assertRaises(HTTPException):
            core.authorize(
                action="test.write",
                x_salus_passphrase="salus-secure",
                x_salus_role="family",
                allowed_roles={"family"},
            )

    def test_plugin_permission_model(self):
        core = SecurityCore()
        with self.assertRaises(HTTPException):
            core.authorize(
                action="plugins.permission.enable",
                x_salus_passphrase="salus-secure",
                x_salus_role="readonly",
                plugin="investor_intelligence",
                allowed_roles={"commander", "agent"},
            )

        ctx = core.authorize(
            action="plugins.permission.enable",
            x_salus_passphrase="salus-secure",
            x_salus_role="commander",
            plugin="investor_intelligence",
            allowed_roles={"commander", "agent"},
        )
        self.assertEqual(ctx.role, "commander")

    def test_audit_log_records_actions(self):
        core = SecurityCore()
        core.reset_audit()
        core.authorize(
            action="audit.sample",
            x_salus_passphrase="salus-secure",
            x_salus_role="commander",
            allowed_roles={"commander"},
        )
        entries = core.audit(limit=10)
        self.assertGreaterEqual(len(entries), 1)
        self.assertEqual(entries[-1]["action"], "audit.sample")
        self.assertTrue(entries[-1]["allowed"])

    def test_security_endpoints(self):
        status_payload = asyncio.run(
            security_status(
                x_salus_passphrase="salus-secure",
                x_salus_token=None,
                x_salus_role="readonly",
            )
        )
        self.assertIn("zero_trust", status_payload)

        audit_payload = asyncio.run(
            security_audit(
                limit=20,
                x_salus_passphrase="salus-secure",
                x_salus_token=None,
                x_salus_role="readonly",
            )
        )
        self.assertEqual(audit_payload["status"], "ok")
        self.assertIn("audit", audit_payload)

        lockdown_payload = asyncio.run(
            security_lockdown(
                request=DummyRequest({"enabled": True}),
                x_salus_passphrase="salus-secure",
                x_salus_token=None,
                x_salus_role="commander",
            )
        )
        self.assertEqual(lockdown_payload["status"], "updated")
        self.assertTrue(lockdown_payload["lockdown"])

        unlock_payload = asyncio.run(
            security_unlock(
                x_salus_passphrase="salus-secure",
                x_salus_token=None,
                x_salus_role="commander",
            )
        )
        self.assertEqual(unlock_payload["status"], "updated")
        self.assertFalse(unlock_payload["lockdown"])


if __name__ == "__main__":
    unittest.main()
