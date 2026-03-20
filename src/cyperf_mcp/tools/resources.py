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

    # ── Full-featured list (apps & attacks have search/sort/filter) ──

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

    # ── 1A: Unified browse for simple (take, skip) resource types ──

    _BROWSE_DISPATCH = {
        "app_types":         "get_resources_application_types",
        "attack_categories": "get_resources_attack_categories",
        "auth_profiles":     "get_resources_auth_profiles",
        "captures":          "get_resources_captures",
        "tls_certs":         "get_resources_certificates",
        "custom_fuzzing":    "get_resources_custom_fuzzing_scripts",
        "payloads":          "get_resources_payloads",
        "pcaps":             "get_resources_pcaps",
        "http_profiles":     "get_resources_http_profiles",
    }

    # SDK endpoint path for raw REST fallback when Pydantic deserialization fails
    _BROWSE_PATHS = {
        "app_types":         "/api/v2/resources/application-types",
        "attack_categories": "/api/v2/resources/attack-categories",
        "auth_profiles":     "/api/v2/resources/auth-profiles",
        "captures":          "/api/v2/resources/captures",
        "tls_certs":         "/api/v2/resources/certificates",
        "custom_fuzzing":    "/api/v2/resources/custom-fuzzing-scripts",
        "payloads":          "/api/v2/resources/payloads",
        "pcaps":             "/api/v2/resources/pcaps",
        "http_profiles":     "/api/v2/resources/http-profiles",
    }

    def browse(self, resource_type: str, take=None, skip=None):
        method_name = self._BROWSE_DISPATCH.get(resource_type)
        if not method_name:
            return {"error": True, "message": f"Unknown resource_type '{resource_type}'. "
                    f"Valid types: {', '.join(sorted(self._BROWSE_DISPATCH))}"}
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            try:
                method = getattr(self.api, method_name)
                result = method(**kwargs)
                return serialize_response(result)
            except cyperf.ApiException:
                raise
            except Exception:
                # Pydantic deserialization failure — fall back to raw REST
                return self._browse_raw_fallback(resource_type, kwargs)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def _browse_raw_fallback(self, resource_type, kwargs):
        """Raw REST fallback for resource types with SDK deserialization bugs."""
        import json
        path = self._BROWSE_PATHS.get(resource_type)
        if not path:
            return {"error": True, "message": f"No REST fallback for '{resource_type}'"}
        api_client = self.api.api_client
        host = api_client.configuration.host
        auth = {"Authorization": f"Bearer {api_client.configuration.access_token}",
                "Accept": "application/json"}
        query = "&".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)
        url = f"{host}{path}" + (f"?{query}" if query else "")
        resp = api_client.rest_client.request("GET", url, headers=auth)
        resp.read()
        raw = resp.data if isinstance(resp.data, str) else resp.data.decode("utf-8")
        return json.loads(raw)

    # ── 1B: Unified get-by-ID ──

    _GET_DISPATCH = {
        "app":      "get_resources_app_by_id",
        "attack":   "get_resources_attack_by_id",
        "capture":  "get_resources_capture_by_id",
        "tls_cert": "get_resources_certificate_by_id",
    }

    def get(self, resource_type: str, resource_id: str):
        method_name = self._GET_DISPATCH.get(resource_type)
        if not method_name:
            return {"error": True, "message": f"Unknown resource_type '{resource_type}'. "
                    f"Valid types: {', '.join(sorted(self._GET_DISPATCH))}"}
        try:
            method = getattr(self.api, method_name)
            result = method(resource_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    # ── 1C: Unified delete ──

    _DELETE_DISPATCH = {
        "capture":  ("delete_resources_capture",         "Capture"),
        "tls_cert": ("delete_resources_tls_certificate", "TLS certificate"),
        "tls_key":  ("delete_resources_tls_key",         "TLS key"),
    }

    def delete(self, resource_type: str, resource_id: str):
        entry = self._DELETE_DISPATCH.get(resource_type)
        if not entry:
            return {"error": True, "message": f"Unknown resource_type '{resource_type}'. "
                    f"Valid types: {', '.join(sorted(self._DELETE_DISPATCH))}"}
        method_name, label = entry
        try:
            method = getattr(self.api, method_name)
            method(resource_id)
            return {"result": f"{label} {resource_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    # ── 1D: Unified search (client-side substring match) ──

    _SEARCH_DISPATCH = {
        "apps":    "get_resources_apps",
        "attacks": "get_resources_attacks",
    }

    def search(self, resource_type: str, query: str):
        method_name = self._SEARCH_DISPATCH.get(resource_type)
        if not method_name:
            return {"error": True, "message": f"Unknown resource_type '{resource_type}'. "
                    f"Valid types: {', '.join(sorted(self._SEARCH_DISPATCH))}"}
        try:
            method = getattr(self.api, method_name)
            all_items = method()
            q = query.lower()
            matches = []
            for item in all_items:
                name = getattr(item, 'name', '') or ''
                desc = getattr(item, 'description', '') or ''
                if q in name.lower() or q in desc.lower():
                    matches.append({
                        "name": name,
                        "id": getattr(item, 'id', None),
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

    # ── Full-featured list tools (apps & attacks keep their own tools due to
    #    search_col/search_val/filter_mode/sort params) ──

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

    # ── 1A: Unified browse for simple resource types ──

    @mcp.tool()
    def resources_browse(resource_type: str, take: int = None, skip: int = None) -> dict:
        """[Resources] Browse a resource catalog by type.

        Lists items from a specific resource category. For apps and attacks
        (which support full search/filter), use resources_list_apps or resources_list_attacks instead.

        Args:
            resource_type: One of: app_types, attack_categories, auth_profiles,
                          captures, tls_certs, custom_fuzzing, payloads, pcaps, http_profiles.
                          Note: tls_certs lists certificate *files*, not cipher configuration.
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.browse(resource_type, take, skip)

    # ── 1B: Unified get-by-ID ──

    @mcp.tool()
    def resources_get(resource_type: str, resource_id: str) -> dict:
        """[Resources] Get details of a specific resource by type and ID.

        Args:
            resource_type: One of: app, attack, capture, tls_cert
            resource_id: The resource identifier
        """
        return tools.get(resource_type, resource_id)

    # ── 1C: Unified delete ──

    @mcp.tool()
    def resources_delete(resource_type: str, resource_id: str) -> dict:
        """[Resources] Delete a resource by type and ID.

        Args:
            resource_type: One of: capture, tls_cert, tls_key
            resource_id: The resource identifier to delete
        """
        return tools.delete(resource_type, resource_id)

    # ── 1D: Unified search (client-side substring match) ──

    @mcp.tool()
    def resources_search(resource_type: str, query: str) -> dict:
        """[Resources] Search resources by substring match against name or description.

        Fetches all items and filters client-side (case-insensitive).
        Returns compact results with name, id, and description.

        Args:
            resource_type: One of: apps, attacks
            query: Search string to match (e.g. 'LLM', 'streaming', 'CVE-2024', 'injection')
        """
        return tools.search(resource_type, query)
