from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, build_list_kwargs


class ResourceTools:
    """Application resource tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.ApplicationResourcesApi:
        return self._client.resources

    def list_apps(self, take=None, skip=None, search_col=None, search_val=None,
                  filter_mode=None, sort=None):
        try:
            kwargs = build_list_kwargs(take, skip, search_col, search_val, filter_mode, sort)
            result = self.api.get_resources_apps(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_app(self, app_id: str):
        try:
            result = self.api.get_resources_app_by_id(app_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_app_types(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_resources_application_types(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_attacks(self, take=None, skip=None, search_col=None, search_val=None,
                     filter_mode=None, sort=None):
        try:
            kwargs = build_list_kwargs(take, skip, search_col, search_val, filter_mode, sort)
            result = self.api.get_resources_attacks(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_attack(self, attack_id: str):
        try:
            result = self.api.get_resources_attack_by_id(attack_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_attack_categories(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.api.get_resources_attack_categories(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_auth_profiles(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_resources_auth_profiles(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_captures(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_resources_captures(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_capture(self, capture_id: str):
        try:
            result = self.api.get_resources_capture_by_id(capture_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete_capture(self, capture_id: str):
        try:
            self.api.delete_resources_capture(capture_id)
            return {"result": f"Capture {capture_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_certificates(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_resources_certificates(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_certificate(self, cert_id: str):
        try:
            result = self.api.get_resources_certificate_by_id(cert_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete_tls_cert(self, tls_cert_id: str):
        try:
            self.api.delete_resources_tls_certificate(tls_cert_id)
            return {"result": f"TLS certificate {tls_cert_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete_tls_key(self, tls_key_id: str):
        try:
            self.api.delete_resources_tls_key(tls_key_id)
            return {"result": f"TLS key {tls_key_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_custom_fuzzing(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_resources_custom_fuzzing_scripts(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_payloads(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.api.get_resources_payloads(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_pcaps(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            result = self.api.get_resources_pcap(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def list_http_profiles(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_resources_http_profiles(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


    def search_apps(self, query: str):
        """Search apps by substring match on name or description (case-insensitive)."""
        try:
            all_apps = self.api.get_resources_apps()
            q = query.lower()
            matches = []
            for app in all_apps:
                name = getattr(app, 'name', '') or ''
                desc = getattr(app, 'description', '') or ''
                if q in name.lower() or q in desc.lower():
                    matches.append({
                        "name": name,
                        "id": getattr(app, 'id', None),
                        "description": desc,
                    })
            return {"count": len(matches), "matches": matches}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def search_attacks(self, query: str):
        """Search attacks by substring match on name or description (case-insensitive)."""
        try:
            all_attacks = self.api.get_resources_attacks()
            q = query.lower()
            matches = []
            for attack in all_attacks:
                name = getattr(attack, 'name', '') or ''
                desc = getattr(attack, 'description', '') or ''
                if q in name.lower() or q in desc.lower():
                    matches.append({
                        "name": name,
                        "id": getattr(attack, 'id', None),
                        "description": desc,
                    })
            return {"count": len(matches), "matches": matches}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all resource tools with the MCP server."""
    tools = ResourceTools(client)

    @mcp.tool()
    def resources_list_apps(take: int = None, skip: int = None,
                            search_col: str = None, search_val: str = None,
                            filter_mode: str = None, sort: str = None) -> dict:
        """[Resources] List available applications for traffic generation with optional search.

        Use search_col='name', search_val='HTTP', filter_mode='exact' to find apps by name.

        Args:
            take: Number of results to return
            skip: Number of results to skip
            search_col: Column to search (e.g. 'name')
            search_val: Value to search for (e.g. 'HTTP')
            filter_mode: Filter mode ('contains', 'exact', etc.)
            sort: Sort expression
        """
        return tools.list_apps(take, skip, search_col, search_val, filter_mode, sort)

    @mcp.tool()
    def resources_get_app(app_id: str) -> dict:
        """[Resources] Get application details by ID.

        Args:
            app_id: The application identifier
        """
        return tools.get_app(app_id)

    @mcp.tool()
    def resources_list_app_types(take: int = None, skip: int = None) -> dict:
        """[Resources] List application types (HTTP, TLS, etc.).

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_app_types(take, skip)

    @mcp.tool()
    def resources_list_attacks(take: int = None, skip: int = None,
                               search_col: str = None, search_val: str = None,
                               filter_mode: str = None, sort: str = None) -> dict:
        """[Resources] List available attacks/strikes for security testing with optional search.

        Use search_col='name', search_val='CVE-2021', filter_mode='contains' to find attacks.

        Args:
            take: Number of results to return
            skip: Number of results to skip
            search_col: Column to search (e.g. 'name', 'category')
            search_val: Value to search for
            filter_mode: Filter mode ('contains', 'exact', etc.)
            sort: Sort expression
        """
        return tools.list_attacks(take, skip, search_col, search_val, filter_mode, sort)

    @mcp.tool()
    def resources_get_attack(attack_id: str) -> dict:
        """[Resources] Get attack/strike details by ID.

        Args:
            attack_id: The attack identifier
        """
        return tools.get_attack(attack_id)

    @mcp.tool()
    def resources_list_attack_categories(take: int = None, skip: int = None) -> dict:
        """[Resources] List attack categories.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_attack_categories(take, skip)

    @mcp.tool()
    def resources_list_auth_profiles(take: int = None, skip: int = None) -> dict:
        """[Resources] List authentication profiles.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_auth_profiles(take, skip)

    @mcp.tool()
    def resources_list_captures(take: int = None, skip: int = None) -> dict:
        """[Resources] List packet captures.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_captures(take, skip)

    @mcp.tool()
    def resources_get_capture(capture_id: str) -> dict:
        """[Resources] Get packet capture details by ID.

        Args:
            capture_id: The capture identifier
        """
        return tools.get_capture(capture_id)

    @mcp.tool()
    def resources_delete_capture(capture_id: str) -> dict:
        """[Resources] Delete a packet capture.

        Args:
            capture_id: The capture identifier to delete
        """
        return tools.delete_capture(capture_id)

    @mcp.tool()
    def resources_list_tls_certs(take: int = None, skip: int = None) -> dict:
        """[Resources] List TLS certificates.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_certificates(take, skip)

    @mcp.tool()
    def resources_get_tls_cert(cert_id: str) -> dict:
        """[Resources] Get TLS certificate details by ID.

        Args:
            cert_id: The certificate identifier
        """
        return tools.get_certificate(cert_id)

    @mcp.tool()
    def resources_delete_tls_cert(tls_cert_id: str) -> dict:
        """[Resources] Delete a TLS certificate.

        Args:
            tls_cert_id: The TLS certificate identifier to delete
        """
        return tools.delete_tls_cert(tls_cert_id)

    @mcp.tool()
    def resources_list_custom_fuzzing(take: int = None, skip: int = None) -> dict:
        """[Resources] List custom fuzzing scripts.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_custom_fuzzing(take, skip)

    @mcp.tool()
    def resources_list_payloads(take: int = None, skip: int = None) -> dict:
        """[Resources] List payloads.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_payloads(take, skip)

    @mcp.tool()
    def resources_list_pcaps(take: int = None, skip: int = None) -> dict:
        """[Resources] List PCAP files.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_pcaps(take, skip)

    @mcp.tool()
    def resources_list_http_profiles(take: int = None, skip: int = None) -> dict:
        """[Resources] List HTTP profiles.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list_http_profiles(take, skip)

    @mcp.tool()
    def resources_search_apps(query: str) -> dict:
        """[Resources] Search applications by substring match against name or description.

        Fetches all apps and filters client-side (case-insensitive).
        Returns compact results with name, id, and description.

        Args:
            query: Search string to match against app name or description (e.g. 'LLM', 'streaming')
        """
        return tools.search_apps(query)

    @mcp.tool()
    def resources_search_attacks(query: str) -> dict:
        """[Resources] Search attacks by substring match against name or description.

        Fetches all attacks and filters client-side (case-insensitive).
        Returns compact results with name, id, and description.

        Args:
            query: Search string to match against attack name or description (e.g. 'LLM', 'injection', 'CVE-2024')
        """
        return tools.search_attacks(query)
