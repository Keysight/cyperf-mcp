from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, poll_async_operation


class TestOpsTools:
    """Test operation tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.TestOperationsApi:
        return self._client.test_ops

    @property
    def sessions_api(self) -> cyperf.SessionsApi:
        return self._client.sessions

    def start(self, session_id: str):
        try:
            result = self.api.start_test_run_start(session_id)
            return poll_async_operation(
                result,
                lambda op_id: self.api.poll_test_run_start(session_id, op_id),
            )
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def stop(self, session_id: str):
        try:
            result = self.api.start_test_run_stop(session_id)
            return poll_async_operation(
                result,
                lambda op_id: self.api.poll_test_run_stop(session_id, op_id),
            )
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def abort(self, session_id: str):
        try:
            result = self.api.start_test_run_abort(session_id)
            return poll_async_operation(
                result,
                lambda op_id: self.api.poll_test_run_abort(session_id, op_id),
            )
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def calibrate_start(self, session_id: str):
        try:
            result = self.api.start_test_calibrate_start(session_id)
            return poll_async_operation(
                result,
                lambda op_id: self.api.poll_test_calibrate_start(session_id, op_id),
            )
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def calibrate_stop(self, session_id: str):
        try:
            result = self.api.start_test_calibrate_stop(session_id)
            return poll_async_operation(
                result,
                lambda op_id: self.api.poll_test_calibrate_stop(session_id, op_id),
            )
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def init(self, session_id: str):
        try:
            result = self.sessions_api.start_session_test_init(session_id)
            return poll_async_operation(
                result,
                lambda op_id: self.sessions_api.poll_session_test_init(session_id, op_id),
            )
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def end(self, session_id: str):
        try:
            result = self.sessions_api.start_session_test_end(session_id)
            return poll_async_operation(
                result,
                lambda op_id: self.sessions_api.poll_session_test_end(session_id, op_id),
            )
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def prepare(self, session_id: str):
        try:
            result = self.sessions_api.start_session_prepare_test(session_id)
            return poll_async_operation(
                result,
                lambda op_id: self.sessions_api.poll_session_prepare_test(session_id, op_id),
            )
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all test operation tools with the MCP server."""
    tools = TestOpsTools(client)

    @mcp.tool()
    def test_start(session_id: str) -> dict:
        """Start a test run for a session. Polls until the test is running.

        Args:
            session_id: The session identifier
        """
        return tools.start(session_id)

    @mcp.tool()
    def test_stop(session_id: str) -> dict:
        """Stop a running test gracefully.

        Args:
            session_id: The session identifier
        """
        return tools.stop(session_id)

    @mcp.tool()
    def test_abort(session_id: str) -> dict:
        """Abort a test run immediately.

        Args:
            session_id: The session identifier
        """
        return tools.abort(session_id)

    @mcp.tool()
    def test_calibrate_start(session_id: str) -> dict:
        """Start test calibration.

        Args:
            session_id: The session identifier
        """
        return tools.calibrate_start(session_id)

    @mcp.tool()
    def test_calibrate_stop(session_id: str) -> dict:
        """Stop test calibration.

        Args:
            session_id: The session identifier
        """
        return tools.calibrate_stop(session_id)

    @mcp.tool()
    def test_init(session_id: str) -> dict:
        """Initialize a test (allocate resources, prepare agents).

        Args:
            session_id: The session identifier
        """
        return tools.init(session_id)

    @mcp.tool()
    def test_end(session_id: str) -> dict:
        """End a test and release resources.

        Args:
            session_id: The session identifier
        """
        return tools.end(session_id)

    @mcp.tool()
    def test_prepare(session_id: str) -> dict:
        """Prepare a test (pre-flight validation and setup).

        Args:
            session_id: The session identifier
        """
        return tools.prepare(session_id)
