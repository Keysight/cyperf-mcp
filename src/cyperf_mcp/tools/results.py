from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, await_and_serialize, build_list_kwargs


class ResultTools:
    """Test result tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.TestResultsApi:
        return self._client.results

    @property
    def reports_api(self) -> cyperf.ReportsApi:
        return self._client.reports

    def list(self, take=None, skip=None, search_col=None, search_val=None,
             filter_mode=None, sort=None):
        try:
            kwargs = build_list_kwargs(take, skip, search_col, search_val, filter_mode, sort)
            result = self.api.get_results(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get(self, result_id: str):
        try:
            result = self.api.get_result_by_id(result_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete(self, result_id: str):
        try:
            self.api.delete_result(result_id)
            return {"result": f"Result {result_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def batch_delete(self, result_ids: list[str]):
        try:
            items = [
                cyperf.StartAgentsBatchDeleteRequestInner(id=rid)
                for rid in result_ids
            ]
            result = self.api.start_results_batch_delete(start_agents_batch_delete_request_inner=items)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    @property
    def stats_api(self) -> cyperf.StatisticsApi:
        return self._client.statistics

    def get_stats(self, result_id: str, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.stats_api.get_result_stats(result_id, **kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_stat(self, result_id: str, stat_id: str):
        try:
            result = self.stats_api.get_result_stat_by_id(result_id, stat_id)
            # Return only the latest snapshot as a compact table
            columns = result.columns or []
            snapshots = result.snapshots or []
            if not snapshots:
                return {"name": result.name, "columns": columns, "data": []}
            last = snapshots[-1]
            rows = []
            for values in (last.values or []):
                row = {}
                for i, col in enumerate(columns):
                    if i < len(values):
                        val = values[i]
                        if hasattr(val, 'actual_instance'):
                            val = val.actual_instance
                        row[col] = val
                rows.append(row)
            return {"name": result.name, "timestamp": last.timestamp, "data": rows}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_files(self, result_id: str, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.api.get_result_files(result_id, **kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_file(self, result_id: str, file_id: str):
        try:
            result = self.api.get_result_file_by_id(result_id, file_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def download_config(self, result_id: str):
        try:
            result = self.api.get_result_download_result_config(result_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def generate_csv(self, result_id: str):
        try:
            result = self.reports_api.start_result_generate_csv(result_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def generate_pdf(self, result_id: str):
        try:
            result = self.reports_api.start_result_generate_pdf(result_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def generate_all(self, result_id: str):
        try:
            result = self.api.start_result_generate_all(result_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def tags(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_results_tags(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all result tools with the MCP server."""
    tools = ResultTools(client)

    @mcp.tool()
    def results_list(take: int = None, skip: int = None,
                     search_col: str = None, search_val: str = None,
                     filter_mode: str = None, sort: str = None) -> dict:
        """[Results] List test results with optional filtering and search.

        Args:
            take: Number of results to return
            skip: Number of results to skip
            search_col: Column to search (e.g. 'name')
            search_val: Value to search for
            filter_mode: Filter mode ('contains', 'exact', etc.)
            sort: Sort expression
        """
        return tools.list(take, skip, search_col, search_val, filter_mode, sort)

    @mcp.tool()
    def results_get(result_id: str) -> dict:
        """[Results] Get test result details by ID.

        Args:
            result_id: The result identifier
        """
        return tools.get(result_id)

    @mcp.tool()
    def results_delete(result_ids: list[str]) -> dict:
        """[Results] Delete one or more test results.

        Args:
            result_ids: List of result IDs to delete (single or multiple)
        """
        if len(result_ids) == 1:
            return tools.delete(result_ids[0])
        return tools.batch_delete(result_ids)

    @mcp.tool()
    def results_stats(result_id: str, stat_id: str = None,
                      take: int = None, skip: int = None) -> dict:
        """[Results] Get statistics for a test result. Lists all stats, or a specific one by ID.

        When stat_id is given, returns only the latest snapshot as a compact table
        with column names as keys. Use without stat_id first to discover available stat names.

        Args:
            result_id: The result identifier
            stat_id: Optional specific statistic ID (returns all stats if omitted)
            take: Number of stats to return (when listing all)
            skip: Number of stats to skip (when listing all)
        """
        if stat_id:
            return tools.get_stat(result_id, stat_id)
        return tools.get_stats(result_id, take, skip)

    @mcp.tool()
    def results_files(result_id: str, file_id: str = None,
                      take: int = None, skip: int = None) -> dict:
        """[Results] Get files for a test result. Lists all files, or a specific one by ID.

        Args:
            result_id: The result identifier
            file_id: Optional specific file ID (returns all files if omitted)
            take: Number of files to return (when listing all)
            skip: Number of files to skip (when listing all)
        """
        if file_id:
            return tools.get_file(result_id, file_id)
        return tools.get_files(result_id, take, skip)

    @mcp.tool()
    def results_download_config(result_id: str) -> dict:
        """[Results] Download the configuration used for a test result.

        Args:
            result_id: The result identifier
        """
        return tools.download_config(result_id)

    @mcp.tool()
    def results_generate_report(result_id: str, format: str = "all") -> dict:
        """[Results] Generate a report for a test result.

        Args:
            result_id: The result identifier
            format: Report format - 'csv', 'pdf', or 'all' (default: 'all')
        """
        if format == "csv":
            return tools.generate_csv(result_id)
        elif format == "pdf":
            return tools.generate_pdf(result_id)
        return tools.generate_all(result_id)

    @mcp.tool()
    def results_tags(take: int = None, skip: int = None) -> dict:
        """[Results] List result tags.

        Args:
            take: Number of tags to return
            skip: Number of tags to skip
        """
        return tools.tags(take, skip)
