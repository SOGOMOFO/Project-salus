from __future__ import annotations

from typing import Any

from backend.services.legacy_route_adapter import call_main_handler


async def get_records_state() -> Any:
    return await call_main_handler("sprint16_record_management_state")


async def archive_record(request: Any) -> Any:
    return await call_main_handler("sprint16_archive_record", request)


async def delete_record(request: Any) -> Any:
    return await call_main_handler("sprint16_delete_record", request)


async def get_records_page() -> Any:
    return await call_main_handler("sprint16_record_management_page")
