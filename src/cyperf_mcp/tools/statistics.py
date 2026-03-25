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
            if "text/html" in str(e.body or ""):
                return {"error": True, "message": "Stats plugins endpoint returned HTML — this endpoint may not be supported on this controller version"}
            return handle_api_error(e)
        except Exception as e:
            if "text/html" in str(e) or "Expecting value" in str(e):
                return {"error": True, "message": "Stats plugins endpoint returned non-JSON response — this endpoint may not be supported on this controller version"}
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
            result = self.api.start_stats_plugins_ingest(ingest_operation=op)
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
    def stats_plugins(action: str = "list", plugin_id: str = None,
                      plugin_data: dict = None, take: int = None, skip: int = None) -> dict:
        """[Statistics] List, create, or delete stats plugins for external statistics ingestion.

        Args:
            action: 'list' (default), 'create', or 'delete'
            plugin_id: The plugin identifier (required for delete)
            plugin_data: Plugin configuration dict (required for create)
            take: Number of results to return (list only)
            skip: Number of results to skip (list only)
        """
        if action == "list":
            return tools.list_plugins(take, skip)
        elif action == "create":
            if not plugin_data:
                return {"error": True, "message": "plugin_data is required for create"}
            return tools.create_plugin(plugin_data)
        elif action == "delete":
            if not plugin_id:
                return {"error": True, "message": "plugin_id is required for delete"}
            return tools.delete_plugin(plugin_id)
        return {"error": True, "message": f"Unknown action '{action}'. Use 'list', 'create', or 'delete'."}

    @mcp.tool()
    def stats_ingest(operation_data: dict) -> dict:
        """[Statistics] Ingest external statistics via a plugin.

        Args:
            operation_data: Ingestion operation parameters
        """
        return tools.ingest(operation_data)

    # Note: result stats are available via results_stats tool to avoid duplication.
