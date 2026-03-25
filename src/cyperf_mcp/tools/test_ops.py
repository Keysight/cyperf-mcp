from __future__ import annotations

import re

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, await_and_serialize


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

    def _disable_auto_ip_on_segments(self, session_id: str, segment_names: list[str]):
        """Disable ip_auto on the named network segments."""
        session = self.sessions_api.get_session_by_id(session_id)
        disabled = []
        for net_profile in session.config.config.network_profiles:
            for ip_net in net_profile.ip_network_segment:
                name = ip_net.base_model.name
                if name in segment_names and ip_net.ip_ranges[0].base_model.ip_auto:
                    ip_net.ip_ranges[0].ip_auto = False
                    ip_net.update()
                    disabled.append(name)
        return disabled

    def start(self, session_id: str):
        """Start a test run. Auto-fixes NETMASK errors by disabling ip_auto and retrying."""
        try:
            result = self.api.start_test_run_start(session_id=session_id)
            return await_and_serialize(result)
        except Exception as first_err:
            # Check if the failure is a NETMASK error on auto-IP segments
            try:
                test_info = self.sessions_api.get_session_test(session_id)
                details = getattr(test_info.base_model, 'test_details', '') or ''
            except Exception:
                details = ''

            if 'could not find NETMASK' not in details:
                if isinstance(first_err, cyperf.ApiException):
                    return handle_api_error(first_err)
                return handle_exception(first_err)

            # Parse affected segment names from error like "[IP Network 2]"
            affected = re.findall(r"\[([^\]]+)\]", details)
            if not affected:
                return handle_exception(first_err)

            disabled = self._disable_auto_ip_on_segments(session_id, affected)
            if not disabled:
                return handle_exception(first_err)

            # Retry the start after disabling auto IP
            try:
                result = self.api.start_test_run_start(session_id=session_id)
                ret = await_and_serialize(result)
                ret["auto_fix_applied"] = (
                    f"Disabled automatic IP on segments {disabled} "
                    f"due to NETMASK error, then retried successfully"
                )
                return ret
            except cyperf.ApiException as e:
                return handle_api_error(e)
            except Exception as e:
                return handle_exception(e)

    def stop(self, session_id: str):
        """Stop a test run (mirrors utils.stop_test using await_completion)."""
        try:
            result = self.api.start_test_run_stop(session_id=session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def abort(self, session_id: str):
        try:
            result = self.api.start_test_run_abort(session_id=session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def calibrate_start(self, session_id: str):
        try:
            result = self.api.start_test_calibrate_start(session_id=session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def calibrate_stop(self, session_id: str):
        try:
            result = self.api.start_test_calibrate_stop(session_id=session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)



def register(mcp, client: CyPerfClientManager):
    """Register all test operation tools with the MCP server."""
    tools = TestOpsTools(client)

    @mcp.tool()
    def test_start(session_id: str) -> dict:
        """[Test Operations] Start a test run for a session. Polls until the test is running.

        Args:
            session_id: The session identifier
        """
        return tools.start(session_id)

    @mcp.tool()
    def test_stop(session_id: str, force: bool = False) -> dict:
        """[Test Operations] Stop a running test.

        By default performs a graceful stop with ramp-down — use this for normal test
        completion where you want traffic to wind down cleanly and final stats to be collected.

        Set force=True for an immediate abort with no ramp-down — use this when the test
        is stuck, unresponsive, or you need to halt traffic instantly (e.g., unexpected errors,
        runaway load, or emergency shutdown).

        Args:
            session_id: The session identifier
            force: False (default) for graceful stop with ramp-down, True for immediate abort
        """
        if force:
            return tools.abort(session_id)
        return tools.stop(session_id)

    @mcp.tool()
    def test_calibrate(session_id: str, action: str = "start") -> dict:
        """[Test Operations] Start or stop test calibration.

        Args:
            session_id: The session identifier
            action: 'start' or 'stop' (default: 'start')
        """
        if action == "stop":
            return tools.calibrate_stop(session_id)
        return tools.calibrate_start(session_id)

