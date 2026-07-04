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


def resolve_legacy_name(name: str) -> Any:
    """Resolve one shared legacy object by name."""
    namespace = legacy_main_namespace()

    if name not in namespace:
        raise KeyError(f"Legacy name not found: {name}")

    return namespace[name]


def legacy_store_count(store_name: str) -> int:
    """Return a best-effort count for a legacy store object."""
    store = resolve_legacy_name(store_name)

    try:
        return len(store)
    except TypeError:
        return 0


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
