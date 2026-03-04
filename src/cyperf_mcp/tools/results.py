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
            result = self.api.start_results_batch_delete(items=items)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_stats(self, result_id: str, take=None, skip=None):
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

    def get_stat(self, result_id: str, stat_id: str):
        try:
            result = self.api.get_result_stat_by_id(result_id, stat_id)
            return serialize_response(result)
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
    def results_delete(result_id: str) -> dict:
        """[Results] Delete a test result.

        Args:
            result_id: The result identifier to delete
        """
        return tools.delete(result_id)

    @mcp.tool()
    def results_batch_delete(result_ids: list[str]) -> dict:
        """[Results] Batch delete multiple test results.

        Args:
            result_ids: List of result IDs to delete
        """
        return tools.batch_delete(result_ids)

    @mcp.tool()
    def results_get_stats(result_id: str, take: int = None, skip: int = None) -> dict:
        """[Results] Get statistics for a test result.

        Args:
            result_id: The result identifier
            take: Number of stats to return
            skip: Number of stats to skip
        """
        return tools.get_stats(result_id, take, skip)

    @mcp.tool()
    def results_get_stat(result_id: str, stat_id: str) -> dict:
        """[Results] Get a specific statistic by ID from a test result.

        Args:
            result_id: The result identifier
            stat_id: The statistic identifier
        """
        return tools.get_stat(result_id, stat_id)

    @mcp.tool()
    def results_get_files(result_id: str, take: int = None, skip: int = None) -> dict:
        """[Results] List files associated with a test result.

        Args:
            result_id: The result identifier
            take: Number of files to return
            skip: Number of files to skip
        """
        return tools.get_files(result_id, take, skip)

    @mcp.tool()
    def results_get_file(result_id: str, file_id: str) -> dict:
        """[Results] Get a specific result file metadata.

        Args:
            result_id: The result identifier
            file_id: The file identifier
        """
        return tools.get_file(result_id, file_id)

    @mcp.tool()
    def results_download_config(result_id: str) -> dict:
        """[Results] Download the configuration used for a test result.

        Args:
            result_id: The result identifier
        """
        return tools.download_config(result_id)

    @mcp.tool()
    def results_generate_csv(result_id: str) -> dict:
        """[Results] Generate a CSV report for a test result.

        Args:
            result_id: The result identifier
        """
        return tools.generate_csv(result_id)

    @mcp.tool()
    def results_generate_pdf(result_id: str) -> dict:
        """[Results] Generate a PDF report for a test result.

        Args:
            result_id: The result identifier
        """
        return tools.generate_pdf(result_id)

    @mcp.tool()
    def results_generate_all(result_id: str) -> dict:
        """[Results] Generate all report formats (CSV + PDF) for a test result.

        Args:
            result_id: The result identifier
        """
        return tools.generate_all(result_id)

    @mcp.tool()
    def results_tags(take: int = None, skip: int = None) -> dict:
        """[Results] List result tags.

        Args:
            take: Number of tags to return
            skip: Number of tags to skip
        """
        return tools.tags(take, skip)
