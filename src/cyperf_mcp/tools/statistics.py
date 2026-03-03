from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, poll_async_operation


class StatisticsTools:
    """Statistics tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.StatisticsApi:
        return self._client.statistics

    def list_plugins(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_stats_plugins(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def create_plugin(self, plugin_data: dict):
        try:
            plugin = cyperf.Plugin(**plugin_data)
            result = self.api.create_stats_plugins(plugins=[plugin])
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete_plugin(self, plugin_id: str):
        try:
            self.api.delete_stats_plugin(plugin_id)
            return {"result": f"Stats plugin {plugin_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def ingest(self, operation_data: dict):
        try:
            op = cyperf.IngestOperation(**operation_data)
            result = self.api.start_stats_plugins_ingest(operation=op)
            return poll_async_operation(result, self.api.poll_stats_plugins_ingest)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_result_stats(self, result_id: str, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.api.get_result_stats(result_id, **kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_result_stat(self, result_id: str, stat_id: str):
        try:
            result = self.api.get_result_stat_by_id(result_id, stat_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all statistics tools with the MCP server."""
    tools = StatisticsTools(client)

    @mcp.tool()
    def stats_list_plugins(take: int = None, skip: int = None) -> dict:
        """List stats plugins.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_plugins(take, skip)

    @mcp.tool()
    def stats_create_plugin(plugin_data: dict) -> dict:
        """Create a stats plugin for external statistics ingestion.

        Args:
            plugin_data: Plugin configuration (e.g. name, type, endpoint)
        """
        return tools.create_plugin(plugin_data)

    @mcp.tool()
    def stats_delete_plugin(plugin_id: str) -> dict:
        """Delete a stats plugin.

        Args:
            plugin_id: The plugin identifier to delete
        """
        return tools.delete_plugin(plugin_id)

    @mcp.tool()
    def stats_ingest(operation_data: dict) -> dict:
        """Ingest external statistics via a plugin.

        Args:
            operation_data: Ingestion operation parameters
        """
        return tools.ingest(operation_data)

    @mcp.tool()
    def stats_get_result_stats(result_id: str, take: int = None, skip: int = None) -> dict:
        """Get statistics for a test result.

        Args:
            result_id: The test result identifier
            take: Number of stats to return
            skip: Number of stats to skip
        """
        return tools.get_result_stats(result_id, take, skip)

    @mcp.tool()
    def stats_get_result_stat(result_id: str, stat_id: str) -> dict:
        """Get a specific statistic by name from a test result.

        Args:
            result_id: The test result identifier
            stat_id: The statistic name/identifier
        """
        return tools.get_result_stat(result_id, stat_id)
