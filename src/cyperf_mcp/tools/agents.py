from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, await_and_serialize, build_list_kwargs


class AgentTools:
    """Agent management tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.AgentsApi:
        return self._client.agents

    def list(self, take=None, skip=None, search_col=None, search_val=None,
             filter_mode=None, sort=None, exclude_offline=None):
        try:
            kwargs = build_list_kwargs(take, skip, search_col, search_val,
                                       filter_mode, sort, exclude_offline=exclude_offline)
            result = self.api.get_agents(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get(self, agent_id: str):
        try:
            result = self.api.get_agent_by_id(agent_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete(self, agent_id: str):
        try:
            self.api.delete_agent(agent_id)
            return {"result": f"Agent {agent_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def update(self, agent_id: str, properties: dict):
        try:
            agent = cyperf.Agent(**properties)
            result = self.api.patch_agent(agent_id, agent=agent)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def batch_delete(self, agent_ids: list[str]):
        try:
            items = [
                cyperf.StartAgentsBatchDeleteRequestInner(id=aid)
                for aid in agent_ids
            ]
            result = self.api.start_agents_batch_delete(start_agents_batch_delete_request_inner=items)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def reserve(self, agent_ids: list[str]):
        try:
            op = cyperf.ReserveOperationInput(agent_ids=agent_ids)
            result = self.api.start_agents_reserve(operation=op)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def release(self, agent_ids: list[str]):
        try:
            op = cyperf.ReleaseOperationInput(agent_ids=agent_ids)
            result = self.api.start_agents_release(operation=op)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def reboot(self, agent_ids: list[str]):
        try:
            op = cyperf.RebootOperationInput(agent_ids=agent_ids)
            result = self.api.start_agents_reboot(operation=op)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_dpdk(self, agent_ids: list[str], enabled: bool):
        try:
            op = cyperf.SetDpdkModeOperationInput(agent_ids=agent_ids, enabled=enabled)
            result = self.api.start_agents_set_dpdk_mode(operation=op)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_ntp(self, agent_ids: list[str], ntp_server: str):
        try:
            op = cyperf.SetNtpOperationInput(agent_ids=agent_ids, ntp_server=ntp_server)
            result = self.api.start_agents_set_ntp(operation=op)
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
            result = self.api.get_agents_tags(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def export_files(self, agent_ids: list[str], file_type: str = None):
        try:
            op = cyperf.ExportFilesOperationInput(agent_ids=agent_ids)
            if file_type:
                op.file_type = file_type
            result = self.api.start_agents_export_files(operation=op)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all agent tools with the MCP server."""
    tools = AgentTools(client)

    @mcp.tool()
    def agents_list(take: int = None, skip: int = None,
                    search_col: str = None, search_val: str = None,
                    filter_mode: str = None, sort: str = None,
                    exclude_offline: str = None) -> dict:
        """[Agents] List all CyPerf agents with optional filtering and search.

        Args:
            take: Number of results to return
            skip: Number of results to skip
            search_col: Column to search (e.g. 'name', 'ip')
            search_val: Value to search for
            filter_mode: Filter mode ('contains', 'exact', etc.)
            sort: Sort expression
            exclude_offline: Set to 'true' to exclude offline agents
        """
        return tools.list(take, skip, search_col, search_val, filter_mode, sort, exclude_offline)

    @mcp.tool()
    def agents_get(agent_id: str) -> dict:
        """[Agents] Get details of a specific CyPerf agent by ID.

        Args:
            agent_id: The agent identifier
        """
        return tools.get(agent_id)

    @mcp.tool()
    def agents_delete(agent_ids: list[str]) -> dict:
        """[Agents] Delete one or more CyPerf agents.

        Args:
            agent_ids: List of agent IDs to delete (single or multiple)
        """
        if len(agent_ids) == 1:
            return tools.delete(agent_ids[0])
        return tools.batch_delete(agent_ids)

    @mcp.tool()
    def agents_update(agent_id: str, properties: dict) -> dict:
        """[Agents] Update agent properties.

        Args:
            agent_id: The agent identifier
            properties: Dict of agent properties to update (e.g. name, tags)
        """
        return tools.update(agent_id, properties)

    @mcp.tool()
    def agents_reserve(agent_ids: list[str]) -> dict:
        """[Agents] Reserve agents for testing.

        Args:
            agent_ids: List of agent IDs to reserve
        """
        return tools.reserve(agent_ids)

    @mcp.tool()
    def agents_release(agent_ids: list[str]) -> dict:
        """[Agents] Release reserved agents.

        Args:
            agent_ids: List of agent IDs to release
        """
        return tools.release(agent_ids)

    @mcp.tool()
    def agents_reboot(agent_ids: list[str]) -> dict:
        """[Agents] Reboot agents.

        Args:
            agent_ids: List of agent IDs to reboot
        """
        return tools.reboot(agent_ids)

    @mcp.tool()
    def agents_set_dpdk(agent_ids: list[str], enabled: bool) -> dict:
        """[Agents] Set DPDK mode on agents.

        Args:
            agent_ids: List of agent IDs
            enabled: Whether to enable DPDK mode
        """
        return tools.set_dpdk(agent_ids, enabled)

    @mcp.tool()
    def agents_set_ntp(agent_ids: list[str], ntp_server: str) -> dict:
        """[Agents] Set NTP configuration on agents.

        Args:
            agent_ids: List of agent IDs
            ntp_server: NTP server address
        """
        return tools.set_ntp(agent_ids, ntp_server)

    @mcp.tool()
    def agents_tags(take: int = None, skip: int = None) -> dict:
        """[Agents] List agent tags.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.tags(take, skip)

    @mcp.tool()
    def agents_export_files(agent_ids: list[str], file_type: str = None) -> dict:
        """[Agents] Export agent files (logs, configs, etc.).

        Args:
            agent_ids: List of agent IDs to export files from
            file_type: Type of files to export
        """
        return tools.export_files(agent_ids, file_type)
