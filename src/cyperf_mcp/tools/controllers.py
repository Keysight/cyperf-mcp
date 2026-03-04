from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, poll_async_operation


class ControllerTools:
    """Controller management tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.AgentsApi:
        return self._client.controllers

    def list(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_controllers(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get(self, controller_id: str):
        try:
            result = self.api.get_controller_by_id(controller_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_nodes(self, controller_id: str, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.api.get_controller_compute_nodes(controller_id, **kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_node(self, controller_id: str, node_id: str):
        try:
            result = self.api.get_controller_compute_node_by_id(controller_id, node_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_ports(self, controller_id: str, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.api.get_compute_node_ports(controller_id, **kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_port(self, controller_id: str, port_id: str):
        try:
            result = self.api.get_compute_node_port_by_id(controller_id, port_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_app(self, controller_id: str, app_id: str):
        try:
            op = cyperf.SetAppOperation(controller_id=controller_id, app_id=app_id)
            result = self.api.start_controllers_set_app(operation=op)
            return poll_async_operation(result, self.api.poll_controllers_set_app)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def clear_ports(self, controller_id: str):
        try:
            op = cyperf.ClearPortsOwnershipOperation(controller_id=controller_id)
            result = self.api.start_controllers_clear_port_ownership(operation=op)
            return poll_async_operation(result, self.api.poll_controllers_clear_port_ownership)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def power_cycle(self, controller_id: str, node_ids: list[str]):
        try:
            op = cyperf.NodesPowerCycleOperation(controller_id=controller_id, node_ids=node_ids)
            result = self.api.start_controllers_power_cycle_nodes(operation=op)
            return poll_async_operation(result, self.api.poll_controllers_power_cycle_nodes)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def reboot_port(self, controller_id: str, port_id: str):
        try:
            op = cyperf.RebootPortsOperation(controller_id=controller_id, port_ids=[port_id])
            result = self.api.start_controllers_reboot_port(operation=op)
            return poll_async_operation(result, self.api.poll_controllers_reboot_port)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_link_state(self, controller_id: str, port_id: str, state: str):
        try:
            op = cyperf.SetLinkStateOperation(
                controller_id=controller_id, port_id=port_id, state=state
            )
            result = self.api.start_controllers_set_port_link_state(operation=op)
            return poll_async_operation(result, self.api.poll_controllers_set_port_link_state)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_aggregation(self, controller_id: str, node_id: str, mode: str):
        try:
            op = cyperf.SetAggregationModeOperation(
                controller_id=controller_id, node_id=node_id, mode=mode
            )
            result = self.api.start_controllers_set_node_aggregation(operation=op)
            return poll_async_operation(result, self.api.poll_controllers_set_node_aggregation)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all controller tools with the MCP server."""
    tools = ControllerTools(client)

    @mcp.tool()
    def controllers_list(take: int = None, skip: int = None) -> dict:
        """[Controllers] List all controllers.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list(take, skip)

    @mcp.tool()
    def controllers_get(controller_id: str) -> dict:
        """[Controllers] Get controller details by ID.

        Args:
            controller_id: The controller identifier
        """
        return tools.get(controller_id)

    @mcp.tool()
    def controllers_nodes(controller_id: str, node_id: str = None,
                          take: int = None, skip: int = None) -> dict:
        """[Controllers] List compute nodes, or get a specific node by ID.

        Args:
            controller_id: The controller identifier
            node_id: Optional node ID (lists all nodes if omitted)
            take: Number of results to return (when listing all)
            skip: Number of results to skip (when listing all)
        """
        if node_id:
            return tools.get_node(controller_id, node_id)
        return tools.list_nodes(controller_id, take, skip)

    @mcp.tool()
    def controllers_ports(controller_id: str, port_id: str = None,
                          take: int = None, skip: int = None) -> dict:
        """[Controllers] List ports on a controller, or get a specific port by ID.

        Args:
            controller_id: The controller identifier
            port_id: Optional port ID (lists all ports if omitted)
            take: Number of results to return (when listing all)
            skip: Number of results to skip (when listing all)
        """
        if port_id:
            return tools.get_port(controller_id, port_id)
        return tools.list_ports(controller_id, take, skip)

    @mcp.tool()
    def controllers_set_app(controller_id: str, app_id: str) -> dict:
        """[Controllers] Set application on a controller.

        Args:
            controller_id: The controller identifier
            app_id: The application identifier to set
        """
        return tools.set_app(controller_id, app_id)

    @mcp.tool()
    def controllers_clear_ports(controller_id: str) -> dict:
        """[Controllers] Clear port ownership on a controller.

        Args:
            controller_id: The controller identifier
        """
        return tools.clear_ports(controller_id)

    @mcp.tool()
    def controllers_power_cycle(controller_id: str, node_ids: list[str]) -> dict:
        """[Controllers] Power cycle compute nodes.

        Args:
            controller_id: The controller identifier
            node_ids: List of node IDs to power cycle
        """
        return tools.power_cycle(controller_id, node_ids)

    @mcp.tool()
    def controllers_reboot_port(controller_id: str, port_id: str) -> dict:
        """[Controllers] Reboot a port on a controller.

        Args:
            controller_id: The controller identifier
            port_id: The port identifier to reboot
        """
        return tools.reboot_port(controller_id, port_id)

    @mcp.tool()
    def controllers_set_link_state(controller_id: str, port_id: str, state: str) -> dict:
        """[Controllers] Set port link state (up/down).

        Args:
            controller_id: The controller identifier
            port_id: The port identifier
            state: The desired link state (e.g. 'up', 'down')
        """
        return tools.set_link_state(controller_id, port_id, state)

    @mcp.tool()
    def controllers_set_aggregation(controller_id: str, node_id: str, mode: str) -> dict:
        """[Controllers] Set node aggregation mode.

        Args:
            controller_id: The controller identifier
            node_id: The compute node identifier
            mode: The aggregation mode to set
        """
        return tools.set_aggregation(controller_id, node_id, mode)
