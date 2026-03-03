from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, poll_async_operation


class SystemTools:
    """System utility tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.UtilsApi:
        return self._client.utils

    def get_time(self):
        try:
            result = self.api.get_time()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_disk_usage(self):
        try:
            result = self.api.get_disk_usage()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_disk_consumers(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.api.get_disk_usage_consumers(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def cleanup_diagnostics(self):
        try:
            result = self.api.start_disk_usage_cleanup_diagnostics()
            return poll_async_operation(result, self.api.poll_disk_usage_cleanup_diagnostics)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def cleanup_logs(self):
        try:
            result = self.api.start_disk_usage_cleanup_logs()
            return poll_async_operation(result, self.api.poll_disk_usage_cleanup_logs)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def cleanup_results(self):
        try:
            result = self.api.start_disk_usage_cleanup_results()
            return poll_async_operation(result, self.api.poll_disk_usage_cleanup_results)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def check_eula(self):
        try:
            result = self.api.check_eulas()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def accept_eula(self):
        try:
            eula = self.api.get_eula()
            summary = cyperf.EulaSummary(accepted=True)
            result = self.api.post_eula(eula=summary)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_log_config(self):
        try:
            result = self.api.get_log_config()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_log_config(self, config_data: dict):
        try:
            config = cyperf.LogConfig(**config_data)
            result = self.api.update_log_config(config=config)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_tags(self):
        try:
            result = self.api.get_docs()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all system tools with the MCP server."""
    tools = SystemTools(client)

    @mcp.tool()
    def system_get_time() -> dict:
        """Get the CyPerf server time."""
        return tools.get_time()

    @mcp.tool()
    def system_get_disk_usage() -> dict:
        """Get disk usage overview for the CyPerf controller."""
        return tools.get_disk_usage()

    @mcp.tool()
    def system_list_disk_consumers(take: int = None, skip: int = None) -> dict:
        """List disk usage consumers (what's using disk space).

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_disk_consumers(take, skip)

    @mcp.tool()
    def system_cleanup_diagnostics() -> dict:
        """Clean up diagnostics data to free disk space."""
        return tools.cleanup_diagnostics()

    @mcp.tool()
    def system_cleanup_logs() -> dict:
        """Clean up log files to free disk space."""
        return tools.cleanup_logs()

    @mcp.tool()
    def system_cleanup_results() -> dict:
        """Clean up old test results to free disk space."""
        return tools.cleanup_results()

    @mcp.tool()
    def system_check_eula() -> dict:
        """Check EULA acceptance status."""
        return tools.check_eula()

    @mcp.tool()
    def system_accept_eula() -> dict:
        """Accept the End User License Agreement."""
        return tools.accept_eula()

    @mcp.tool()
    def system_get_log_config() -> dict:
        """Get the current logging configuration."""
        return tools.get_log_config()

    @mcp.tool()
    def system_set_log_config(config_data: dict) -> dict:
        """Set logging configuration.

        Args:
            config_data: Logging configuration (e.g. level, file settings)
        """
        return tools.set_log_config(config_data)
