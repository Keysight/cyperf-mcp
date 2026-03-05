import time

import cyperf


def serialize_response(obj):
    """Convert cyperf model objects to JSON-serializable dicts.

    Handles SDK DynamicModel/DynamicList wrappers, AnyOf/OneOf wrappers
    (actual_instance), Pydantic models (model_dump), plain lists, and
    scalar values.  Uses model_dump() instead of to_dict() because the
    SDK's to_dict() excludes read-only fields, stripping useful data.
    """
    if obj is None:
        return {"result": None}

    # Unwrap SDK DynamicModel wrappers (have .base_model with the Pydantic model)
    if hasattr(obj, 'base_model') and hasattr(obj, 'api_client'):
        return serialize_response(obj.base_model)

    # Unwrap AnyOf/OneOf response wrappers
    if hasattr(obj, 'actual_instance'):
        return serialize_response(obj.actual_instance)

    # Pydantic v2 models — use model_dump to keep read-only fields
    if hasattr(obj, 'model_dump'):
        return obj.model_dump(by_alias=True, exclude_none=True)

    # Iterables (list, DynamicList, tuple, etc.) — but not str/bytes/dict
    if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, dict)):
        return [serialize_response(item) for item in obj]

    # Dicts pass through
    if isinstance(obj, dict):
        return obj

    # Scalars
    if isinstance(obj, (str, int, float, bool)):
        return {"result": obj}

    if isinstance(obj, (bytes, bytearray)):
        return {"result": "<binary data>", "size": len(obj)}

    return {"result": str(obj)}


def handle_api_error(e: cyperf.ApiException) -> dict:
    """Standardized error response formatting."""
    return {
        "error": True,
        "status": e.status,
        "reason": e.reason,
        "message": e.body if e.body else str(e),
    }


def handle_exception(e: Exception) -> dict:
    """Handle unexpected exceptions."""
    return {"error": True, "message": str(e)}


def build_list_kwargs(take=None, skip=None, search_col=None, search_val=None,
                      filter_mode=None, sort=None, **extra) -> dict:
    """Build kwargs dict for list API calls, omitting None values."""
    kwargs = {}
    if take is not None:
        kwargs["take"] = take
    if skip is not None:
        kwargs["skip"] = skip
    if search_col is not None:
        kwargs["search_col"] = search_col
    if search_val is not None:
        kwargs["search_val"] = search_val
    if filter_mode is not None:
        kwargs["filter_mode"] = filter_mode
    if sort is not None:
        kwargs["sort"] = sort
    for k, v in extra.items():
        if v is not None:
            kwargs[k] = v
    return kwargs


def await_and_serialize(operation) -> dict:
    """Await an async SDK operation using the built-in await_completion() and serialize the result.

    This mirrors the pattern used in cyperf.utils.TestRunner where operations are
    awaited via operation.await_completion() instead of manual polling.
    """
    result = operation.await_completion()
    if result is None:
        return {"result": "completed"}
    return serialize_response(result)


def poll_async_operation(start_result, poll_fn, interval: float = 2, timeout: float = 300) -> dict:
    """Poll an async operation until completion.

    Args:
        start_result: The AsyncOperationResponse from the start_* call.
        poll_fn: Callable that takes operation id and returns AsyncOperationResponse.
        interval: Seconds between polls.
        timeout: Max seconds to wait.

    Returns:
        Serialized final operation status.
    """
    op_id = start_result.id
    elapsed = 0.0
    while elapsed < timeout:
        status = poll_fn(op_id)
        state = status.state if hasattr(status, 'state') else str(status)
        if state in ("completed", "success"):
            return serialize_response(status)
        if state in ("error", "failed"):
            return {
                "error": True,
                "state": state,
                "message": getattr(status, 'message', ''),
                "operation_id": op_id,
            }
        if state == "NOT_FOUND":
            # Operation completed and was cleaned up by the server
            return {"result": "completed", "operation_id": op_id}
        time.sleep(interval)
        elapsed += interval
    return {
        "error": True,
        "message": f"Operation {op_id} timed out after {timeout}s",
        "last_state": serialize_response(start_result),
    }
