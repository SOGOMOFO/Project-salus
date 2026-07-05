from __future__ import annotations

from typing import Any, MutableMapping


def legacy_main_namespace() -> dict[str, Any]:
    """Return backend.main globals while storage extraction is underway.

    Transitional registry: one controlled place for service modules to access
    existing stores/helpers while backend/main.py is decomposed.
    """
    import backend.main as legacy_main

    return dict(vars(legacy_main))


def sync_legacy_globals(target_globals: MutableMapping[str, Any]) -> None:
    """Populate a service namespace with shared stores/helpers.

    Existing names are preserved. Missing names are copied from backend.main.
    """
    for name, value in legacy_main_namespace().items():
        target_globals.setdefault(name, value)


def sync_service_globals(target_globals: MutableMapping[str, Any]) -> None:
    """Preferred Sprint 32 name for syncing shared service dependencies."""
    sync_legacy_globals(target_globals)


def resolve_legacy_name(name: str) -> Any:
    """Resolve one shared legacy object by name."""
    namespace = legacy_main_namespace()

    if name not in namespace:
        raise KeyError(f"Legacy name not found: {name}")

    return namespace[name]


def get_store(store_name: str, default: Any | None = None) -> Any:
    """Return a store-like object by name from the transitional registry."""
    try:
        return resolve_legacy_name(store_name)
    except KeyError:
        return default


def legacy_store_count(store_name: str) -> int:
    """Return a best-effort count for a legacy store object."""
    store = get_store(store_name)

    try:
        return len(store)
    except TypeError:
        return 0


def store_count(store_name: str) -> int:
    """Preferred Sprint 32 store count helper."""
    return legacy_store_count(store_name)


def store_counts(store_names: list[str]) -> dict[str, int]:
    """Return counts for a list of store names."""
    return {store_name: store_count(store_name) for store_name in store_names}


def available_legacy_stores() -> list[str]:
    """List known underscore-prefixed store-like names from backend.main."""
    namespace = legacy_main_namespace()

    candidates = []
    for name, value in namespace.items():
        if not name.startswith("_"):
            continue
        if isinstance(value, (list, dict)):
            candidates.append(name)

    return sorted(candidates)


def normalize_record_mutation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize Records mutation payloads across old and new route contracts."""
    data = dict(payload or {})

    if "group" not in data and "record_type" in data:
        data["group"] = data["record_type"]

    if "id" not in data and "record_id" in data:
        data["id"] = data["record_id"]

    return data


def storage_registry_status() -> dict[str, Any]:
    """Return a small diagnostic status payload for tests and future health checks."""
    stores = available_legacy_stores()

    return {
        "available_store_count": len(stores),
        "available_stores": stores,
    }
