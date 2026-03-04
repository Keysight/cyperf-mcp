from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, await_and_serialize, build_list_kwargs


class ConfigTools:
    """Configuration management tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.ConfigurationsApi:
        return self._client.configs

    def list(self, take=None, skip=None, search_col=None, search_val=None,
             filter_mode=None, sort=None):
        try:
            kwargs = build_list_kwargs(take, skip, search_col, search_val, filter_mode, sort)
            result = self.api.get_configs(**kwargs)
            configs = []
            for c in result:
                configs.append({
                    "id": c.id,
                    "displayName": c.display_name,
                    "owner": c.owner,
                    "lastModified": c.last_modified,
                    "type": c.type,
                })
            # Client-side filter if server didn't apply it
            if search_val and search_col == "name":
                q = search_val.lower()
                if filter_mode == "exact":
                    configs = [c for c in configs if (c.get("displayName") or "").lower() == q]
                else:
                    configs = [c for c in configs if q in (c.get("displayName") or "").lower()]
            return {"data": configs, "totalCount": len(configs)}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get(self, config_id: str):
        try:
            result = self.api.get_config_by_id(config_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def create(self, config_data: dict):
        try:
            config = cyperf.ConfigMetadata(**config_data)
            result = self.api.create_configs(configs=[config])
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete(self, config_id: str):
        try:
            self.api.delete_config(config_id)
            return {"result": f"Configuration {config_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def update(self, config_id: str, properties: dict):
        try:
            config = cyperf.ConfigMetadata(**properties)
            result = self.api.patch_config(config_id, config_metadata=config)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def batch_delete(self, config_ids: list[str]):
        try:
            items = [
                cyperf.StartAgentsBatchDeleteRequestInner(id=cid)
                for cid in config_ids
            ]
            result = self.api.start_configs_batch_delete(items=items)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def import_config(self, file_path: str):
        """Import a configuration file (mirrors utils.load_configuration_file using await_completion)."""
        try:
            result = self.api.start_configs_import(file_path)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def import_all(self, file_path: str):
        try:
            op = cyperf.ImportAllOperation(file_path=file_path)
            result = self.api.start_configs_import_all(operation=op)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def export_all(self, config_ids: list[str] = None):
        try:
            op = cyperf.ExportAllOperation()
            if config_ids:
                op.ids = config_ids
            result = self.api.start_configs_export_all(operation=op)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def categories(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_config_categories(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all configuration tools with the MCP server."""
    tools = ConfigTools(client)

    @mcp.tool()
    def configs_list(take: int = None, skip: int = None,
                     search_col: str = None, search_val: str = None,
                     filter_mode: str = None, sort: str = None) -> dict:
        """[Configurations] List available CyPerf configurations with optional filtering and search.

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
    def configs_get(config_id: str) -> dict:
        """[Configurations] Get a configuration by ID.

        Args:
            config_id: The configuration identifier
        """
        return tools.get(config_id)

    @mcp.tool()
    def configs_create(config_data: dict) -> dict:
        """[Configurations] Create a new configuration.

        Args:
            config_data: Configuration properties (name, description, etc.)
        """
        return tools.create(config_data)

    @mcp.tool()
    def configs_delete(config_ids: list[str]) -> dict:
        """[Configurations] Delete one or more configurations.

        Args:
            config_ids: List of configuration IDs to delete (single or multiple)
        """
        if len(config_ids) == 1:
            return tools.delete(config_ids[0])
        return tools.batch_delete(config_ids)

    @mcp.tool()
    def configs_update(config_id: str, properties: dict) -> dict:
        """[Configurations] Update configuration metadata.

        Args:
            config_id: The configuration identifier
            properties: Dict of properties to update
        """
        return tools.update(config_id, properties)

    @mcp.tool()
    def configs_import(file_path: str) -> dict:
        """[Configurations] Import a configuration from a local file.

        Args:
            file_path: Path to the configuration file to import
        """
        return tools.import_config(file_path)

    @mcp.tool()
    def configs_import_all(file_path: str) -> dict:
        """[Configurations] Import all configurations from a file.

        Args:
            file_path: Path to the file containing configurations
        """
        return tools.import_all(file_path)

    @mcp.tool()
    def configs_export_all(config_ids: list[str] = None) -> dict:
        """[Configurations] Export configurations. If config_ids given, exports those; otherwise all.

        Args:
            config_ids: Optional list of configuration IDs to export
        """
        return tools.export_all(config_ids)

    @mcp.tool()
    def configs_categories(take: int = None, skip: int = None) -> dict:
        """[Configurations] List configuration categories.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.categories(take, skip)
