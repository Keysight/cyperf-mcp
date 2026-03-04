from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception


class BrokerTools:
    """Broker management tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.BrokersApi:
        return self._client.brokers

    def list(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_brokers(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def create(self, broker_data: dict):
        try:
            broker = cyperf.Broker(**broker_data)
            result = self.api.create_brokers(brokers=[broker])
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get(self, broker_id: str):
        try:
            result = self.api.get_broker_by_id(broker_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def update(self, broker_id: str, properties: dict):
        try:
            broker = cyperf.Broker(**properties)
            result = self.api.patch_broker(broker_id, broker=broker)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete(self, broker_id: str):
        try:
            self.api.delete_broker(broker_id)
            return {"result": f"Broker {broker_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all broker tools with the MCP server."""
    tools = BrokerTools(client)

    @mcp.tool()
    def brokers_list(take: int = None, skip: int = None) -> dict:
        """[Brokers] List all brokers.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list(take, skip)

    @mcp.tool()
    def brokers_create(broker_data: dict) -> dict:
        """[Brokers] Create a new broker.

        Args:
            broker_data: Broker properties (e.g. host, port, name)
        """
        return tools.create(broker_data)

    @mcp.tool()
    def brokers_get(broker_id: str) -> dict:
        """[Brokers] Get broker details by ID.

        Args:
            broker_id: The broker identifier
        """
        return tools.get(broker_id)

    @mcp.tool()
    def brokers_update(broker_id: str, properties: dict) -> dict:
        """[Brokers] Update broker properties.

        Args:
            broker_id: The broker identifier
            properties: Dict of broker properties to update
        """
        return tools.update(broker_id, properties)

    @mcp.tool()
    def brokers_delete(broker_id: str) -> dict:
        """[Brokers] Delete a broker.

        Args:
            broker_id: The broker identifier to delete
        """
        return tools.delete(broker_id)
