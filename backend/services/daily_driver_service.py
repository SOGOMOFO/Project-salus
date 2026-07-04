from __future__ import annotations

from typing import Any

from backend.services.legacy_route_adapter import call_main_handler


async def get_daily_driver_state() -> Any:
    return await call_main_handler("sprint15_daily_driver_state")


async def get_daily_driver_page() -> Any:
    return await call_main_handler("sprint15_daily_driver_page")
