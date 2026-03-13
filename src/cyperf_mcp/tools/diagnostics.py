from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception


class DiagnosticsTools:
    """Diagnostics tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.DiagnosticsApi:
        return self._client.diagnostics

    def list_components(self):
        try:
            result = self.api.api_v2_diagnostics_components_get()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def export(self, component_names: list[str] = None):
        try:
            context = None
            if component_names:
                components = [cyperf.DiagnosticComponent(component_name=n) for n in component_names]
                context = cyperf.DiagnosticComponentContext(component_list=components)
            result = self.api.api_v2_diagnostics_operations_export_post(diagnostic_component_context=context)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete(self):
        try:
            self.api.api_v2_diagnostics_operations_delete_delete()
            return {"result": "Diagnostics deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all diagnostics tools with the MCP server."""
    tools = DiagnosticsTools(client)

    @mcp.tool()
    def diagnostics_list_components() -> dict:
        """[Diagnostics] List diagnostic components available for export."""
        return tools.list_components()

    @mcp.tool()
    def diagnostics_export(component_names: list[str] = None) -> dict:
        """[Diagnostics] Export diagnostics. Optionally filter by component names.

        Args:
            component_names: Optional list of component names to export
        """
        return tools.export(component_names)

    @mcp.tool()
    def diagnostics_delete() -> dict:
        """[Diagnostics] Delete all diagnostics data."""
        return tools.delete()
