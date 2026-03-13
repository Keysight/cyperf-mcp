from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, poll_async_operation


class MigrationTools:
    """Data migration tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.DataMigrationApi:
        return self._client.migration

    def export(self, export_data: dict = None):
        try:
            if export_data:
                op = cyperf.ExportPackageOperation(**export_data)
            else:
                op = cyperf.ExportPackageOperation()
            result = self.api.start_controller_migration_export(export_package_operation=op)
            try:
                return poll_async_operation(result, self.api.poll_controller_migration_export)
            except cyperf.ApiException:
                return {"result": "migration export initiated", "operation_id": result.id}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def import_data(self):
        try:
            result = self.api.start_controller_migration_import()
            try:
                return poll_async_operation(result, self.api.poll_controller_migration_import)
            except cyperf.ApiException:
                return {"result": "migration import initiated", "operation_id": result.id}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all migration tools with the MCP server."""
    tools = MigrationTools(client)

    @mcp.tool()
    def migration_export(export_data: dict = None) -> dict:
        """[Migration] Export controller data for migration.

        Args:
            export_data: Optional export parameters (e.g. filter criteria)
        """
        return tools.export(export_data)

    @mcp.tool()
    def migration_import() -> dict:
        """[Migration] Import controller data from a migration package."""
        return tools.import_data()
