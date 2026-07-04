from __future__ import annotations

import inspect
from typing import Any, get_origin


async def call_main_handler(handler_name: str, request: Any | None = None) -> Any:
    """Call a legacy backend.main handler while route ownership is being extracted.

    This keeps route modules thin while Project Salus moves behavior out of
    backend/main.py in controlled steps.
    """
    import backend.main as legacy_main

    handler = getattr(legacy_main, handler_name)
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
