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
    def brokers_manage(action: str, broker_id: str = None, broker_data: dict = None) -> dict:
        """[Brokers] Create, get, update, or delete a broker.

        Args:
            action: One of: 'create', 'get', 'update', 'delete'
            broker_id: The broker identifier (required for get/update/delete)
            broker_data: Broker properties dict (required for create, optional for update)
        """
        if action == "create":
            if not broker_data:
                return {"error": True, "message": "broker_data is required for create"}
            return tools.create(broker_data)
        elif action == "get":
            if not broker_id:
                return {"error": True, "message": "broker_id is required for get"}
            return tools.get(broker_id)
        elif action == "update":
            if not broker_id:
                return {"error": True, "message": "broker_id is required for update"}
            return tools.update(broker_id, broker_data or {})
        elif action == "delete":
            if not broker_id:
                return {"error": True, "message": "broker_id is required for delete"}
            return tools.delete(broker_id)
        return {"error": True, "message": f"Unknown action '{action}'. Use 'create', 'get', 'update', or 'delete'."}
