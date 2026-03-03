import time

import cyperf


def serialize_response(obj):
    """Convert cyperf model objects to JSON-serializable dicts."""
    if obj is None:
        return {"result": None}
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, list):
        return [serialize_response(item) for item in obj]
    if isinstance(obj, dict):
        return obj
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
        if status.state in ("completed", "success"):
            return serialize_response(status)
        if status.state in ("error", "failed"):
            return {
                "error": True,
                "state": status.state,
                "message": status.message,
                "operation_id": op_id,
            }
        time.sleep(interval)
        elapsed += interval
    return {
        "error": True,
        "message": f"Operation {op_id} timed out after {timeout}s",
        "last_state": serialize_response(start_result),
    }
