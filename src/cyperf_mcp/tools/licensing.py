from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception


class LicensingTools:
    """Licensing tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.LicensingApi:
        return self._client.licensing

    @property
    def servers_api(self) -> cyperf.LicenseServersApi:
        return self._client.license_servers

    def list_licenses(self):
        try:
            result = self.api.get_installed_licenses()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_license(self, license_id: int):
        try:
            result = self.api.get_license(license_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def activate(self, activation_code: str):
        try:
            req = cyperf.FulfillmentRequest(activation_code=activation_code)
            result = self.api.activate_licenses(fulfillment_requests=[req])
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def deactivate(self, activation_code: str):
        try:
            req = cyperf.FulfillmentRequest(activation_code=activation_code)
            result = self.api.deactivate_licenses(fulfillment_requests=[req])
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def sync(self):
        try:
            result = self.api.sync_licenses()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_hostid(self):
        try:
            result = self.api.get_hostid()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def reserve_feature(self, license_id: int, feature_name: str, count: int):
        try:
            reservation = cyperf.FeatureReservation(feature_name=feature_name, count=count)
            result = self.api.update_reservation(license_id, reservation=reservation)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def remove_reservation(self, license_id: int):
        try:
            self.api.remove_reservation(license_id)
            return {"result": f"Reservation removed for license {license_id}"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def test_connectivity(self):
        try:
            result = self.api.test_backend_connectivity()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_activation_info(self, activation_code: str):
        try:
            req = cyperf.ActivationCodeRequest(activation_code=activation_code)
            result = self.api.get_activation_code_info(request=req)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_entitlement_info(self, entitlement_code: str):
        try:
            req = cyperf.EntitlementCodeRequest(entitlement_code=entitlement_code)
            result = self.api.get_entitlement_code_info(request=req)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_feature_stats(self):
        try:
            result = self.api.get_counted_feature_stats()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    # License server methods
    def list_servers(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.servers_api.get_license_servers(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def add_server(self, server_data: dict):
        import time
        try:
            server = cyperf.LicenseServerMetadata(**server_data)
            result = self.servers_api.create_license_servers(license_servers=[server])
            if not result:
                return {"result": "License server created (no details returned)"}
            server_id = str(result[0].id)
            latest = result[0]
            for _ in range(60):
                time.sleep(2)
                servers = self.servers_api.get_license_servers()
                for s in servers:
                    if str(s.id) == server_id:
                        latest = s
                        if s.connection_status != 'IN_PROGRESS':
                            return serialize_response(s)
                        break
            # Timed out, return latest state
            return serialize_response(latest)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_server(self, server_id: str):
        try:
            result = self.servers_api.get_license_server_by_id(server_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def update_server(self, server_id: str, properties: dict):
        try:
            server = cyperf.LicenseServerMetadata(**properties)
            result = self.servers_api.patch_license_server(server_id, server=server)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete_server(self, server_id: str):
        try:
            self.servers_api.delete_license_server(server_id)
            return {"result": f"License server {server_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all licensing tools with the MCP server."""
    tools = LicensingTools(client)

    @mcp.tool()
    def licensing_list_licenses() -> dict:
        """[Licensing] List all installed licenses."""
        return tools.list_licenses()

    @mcp.tool()
    def licensing_get_license(license_id: int) -> dict:
        """[Licensing] Get license details by ID.

        Args:
            license_id: The license identifier
        """
        return tools.get_license(license_id)

    @mcp.tool()
    def licensing_activate(activation_code: str) -> dict:
        """[Licensing] Activate a license with an activation code.

        Args:
            activation_code: The activation code
        """
        return tools.activate(activation_code)

    @mcp.tool()
    def licensing_deactivate(activation_code: str) -> dict:
        """[Licensing] Deactivate a license.

        Args:
            activation_code: The activation code to deactivate
        """
        return tools.deactivate(activation_code)

    @mcp.tool()
    def licensing_sync() -> dict:
        """[Licensing] Synchronize licenses with the license server."""
        return tools.sync()

    @mcp.tool()
    def licensing_get_hostid() -> dict:
        """[Licensing] Get the host ID for licensing."""
        return tools.get_hostid()

    @mcp.tool()
    def licensing_reserve_feature(license_id: int, feature_name: str, count: int) -> dict:
        """[Licensing] Reserve a license feature.

        Args:
            license_id: The license identifier
            feature_name: Name of the feature to reserve
            count: Number of units to reserve
        """
        return tools.reserve_feature(license_id, feature_name, count)

    @mcp.tool()
    def licensing_remove_reservation(license_id: int) -> dict:
        """[Licensing] Remove a license reservation.

        Args:
            license_id: The license identifier
        """
        return tools.remove_reservation(license_id)

    @mcp.tool()
    def licensing_test_connectivity() -> dict:
        """[Licensing] Test connectivity to the license backend server."""
        return tools.test_connectivity()

    @mcp.tool()
    def licensing_get_activation_info(activation_code: str) -> dict:
        """[Licensing] Get information about an activation code.

        Args:
            activation_code: The activation code to look up
        """
        return tools.get_activation_info(activation_code)

    @mcp.tool()
    def licensing_get_entitlement_info(entitlement_code: str) -> dict:
        """[Licensing] Get information about an entitlement code.

        Args:
            entitlement_code: The entitlement code to look up
        """
        return tools.get_entitlement_info(entitlement_code)

    @mcp.tool()
    def licensing_get_feature_stats() -> dict:
        """[Licensing] Get counted feature statistics for licenses."""
        return tools.get_feature_stats()

    @mcp.tool()
    def licensing_list_servers(take: int = None, skip: int = None) -> dict:
        """[Licensing] List license servers.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_servers(take, skip)

    @mcp.tool()
    def licensing_add_server(server_data: dict) -> dict:
        """[Licensing] Add a license server.

        IMPORTANT: Always ask the user for username and password before calling this tool.
        The server_data MUST include 'user' and 'password' fields for authentication.

        Args:
            server_data: License server properties. Required keys:
                         host_name (str): IP or hostname of the license server
                         user (str): Username for authentication (ask user if not provided)
                         password (str): Password for authentication (ask user if not provided)
                         trust_new (bool): Set to true to trust the server's identity (default: true)
        """
        if 'trust_new' not in server_data:
            server_data['trust_new'] = True
        return tools.add_server(server_data)

    @mcp.tool()
    def licensing_get_server(server_id: str) -> dict:
        """[Licensing] Get license server details.

        Args:
            server_id: The license server identifier
        """
        return tools.get_server(server_id)

    @mcp.tool()
    def licensing_update_server(server_id: str, properties: dict) -> dict:
        """[Licensing] Update license server properties.

        Args:
            server_id: The license server identifier
            properties: Dict of properties to update
        """
        return tools.update_server(server_id, properties)

    @mcp.tool()
    def licensing_delete_server(server_id: str) -> dict:
        """[Licensing] Delete a license server.

        Args:
            server_id: The license server identifier to delete
        """
        return tools.delete_server(server_id)
