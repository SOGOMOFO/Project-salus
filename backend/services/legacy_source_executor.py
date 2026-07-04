from __future__ import annotations

import inspect
from typing import Any, get_origin

from fastapi import Request
from fastapi.responses import HTMLResponse


async def invoke_legacy_source(source: str, handler_name: str, request: Request | None = None) -> Any:
    """Execute a migrated legacy handler source snapshot against backend.main globals.

    This is a temporary bridge used during backend/main.py decomposition. The route
    behavior now lives in service modules instead of backend/main.py, while still
    preserving old storage dependencies until they are extracted in a later sprint.
    """
    import backend.main as legacy_main

    namespace: dict[str, Any] = dict(vars(legacy_main))
    namespace.update(
        {
            "Any": Any,
            "Request": Request,
            "HTMLResponse": HTMLResponse,
        }
    )

    exec(source, namespace)

    if handler_name not in namespace:
        raise AttributeError(f"Legacy handler not found in source snapshot: {handler_name}")

    handler = namespace[handler_name]
    signature = inspect.signature(handler)
    parameters = list(signature.parameters.values())

    if not parameters:
        result = handler()
    else:
        payload: dict[str, Any] = {}

        if request is not None:
            try:
                payload = await request.json()
            except Exception:
                payload = {}

        if len(parameters) == 1:
            parameter = parameters[0]
            annotation = parameter.annotation

            if isinstance(annotation, str):
                annotation = namespace.get(annotation, annotation)

            origin = get_origin(annotation)

            if (
                annotation is inspect.Signature.empty
                or annotation is Any
                or annotation is dict
                or origin is dict
            ):
                argument = payload
            else:
                try:
                    if hasattr(annotation, "model_validate"):
                        argument = annotation.model_validate(payload)
                    else:
                        argument = annotation(**payload)
                except Exception:
                    argument = payload

            result = handler(argument)
        else:
            kwargs = {}

            for parameter in parameters:
                if parameter.name in payload:
                    kwargs[parameter.name] = payload[parameter.name]
                elif parameter.default is not inspect.Signature.empty:
                    kwargs[parameter.name] = parameter.default
                else:
                    kwargs[parameter.name] = None

            result = handler(**kwargs)

    if inspect.isawaitable(result):
        return await result

    return result
