from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, poll_async_operation


class SessionTools:
    """Session management tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.SessionsApi:
        return self._client.sessions

    def list(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_sessions(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def create(self, session_data: dict):
        try:
            session = cyperf.Session(**session_data)
            result = self.api.create_sessions(sessions=[session])
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get(self, session_id: str):
        try:
            result = self.api.get_session_by_id(session_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete(self, session_id: str):
        try:
            self.api.delete_session(session_id)
            return {"result": f"Session {session_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def update(self, session_id: str, properties: dict):
        try:
            session = cyperf.Session(**properties)
            result = self.api.patch_session(session_id, session=session)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def batch_delete(self, session_ids: list[str]):
        try:
            items = [
                cyperf.StartAgentsBatchDeleteRequestInner(id=sid)
                for sid in session_ids
            ]
            result = self.api.start_sessions_batch_delete(items=items)
            return poll_async_operation(result, self.api.poll_sessions_batch_delete)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_config(self, session_id: str):
        try:
            result = self.api.get_session_config(session_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def save_config(self, session_id: str):
        try:
            result = self.api.start_session_config_save(session_id)
            return poll_async_operation(result, lambda op_id: self.api.poll_session_config_save(session_id, op_id))
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def load_config(self, session_id: str, config_url: str):
        try:
            op = cyperf.LoadConfigOperationInput(config_url=config_url)
            result = self.api.start_session_load_config(session_id, operation=op)
            return poll_async_operation(result, lambda op_id: self.api.poll_session_load_config(session_id, op_id))
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_meta(self, session_id: str):
        try:
            result = self.api.get_session_meta(session_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_test(self, session_id: str):
        try:
            result = self.api.get_session_test(session_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def touch(self, session_id: str):
        try:
            result = self.api.start_session_touch(session_id)
            return poll_async_operation(result, lambda op_id: self.api.poll_session_touch(session_id, op_id))
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def add_applications(self, session_id: str, app_ids: list[str]):
        try:
            op = cyperf.CreateAppOrAttackOperationInput(ids=app_ids)
            result = self.api.start_config_add_applications(session_id, operation=op)
            return poll_async_operation(result, lambda op_id: self.api.poll_config_add_applications(session_id, op_id))
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def test_init(self, session_id: str):
        try:
            result = self.api.start_session_test_init(session_id)
            return poll_async_operation(result, lambda op_id: self.api.poll_session_test_init(session_id, op_id))
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def test_end(self, session_id: str):
        try:
            result = self.api.start_session_test_end(session_id)
            return poll_async_operation(result, lambda op_id: self.api.poll_session_test_end(session_id, op_id))
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def prepare_test(self, session_id: str):
        try:
            result = self.api.start_session_prepare_test(session_id)
            return poll_async_operation(result, lambda op_id: self.api.poll_session_prepare_test(session_id, op_id))
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all session tools with the MCP server."""
    tools = SessionTools(client)

    @mcp.tool()
    def sessions_list(take: int = None, skip: int = None) -> dict:
        """List all CyPerf sessions.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list(take, skip)

    @mcp.tool()
    def sessions_create(session_data: dict) -> dict:
        """Create a new CyPerf session.

        Args:
            session_data: Session properties (e.g. name, description)
        """
        return tools.create(session_data)

    @mcp.tool()
    def sessions_get(session_id: str) -> dict:
        """Get details of a specific session by ID.

        Args:
            session_id: The session identifier
        """
        return tools.get(session_id)

    @mcp.tool()
    def sessions_delete(session_id: str) -> dict:
        """Delete a session.

        Args:
            session_id: The session identifier to delete
        """
        return tools.delete(session_id)

    @mcp.tool()
    def sessions_update(session_id: str, properties: dict) -> dict:
        """Update session properties.

        Args:
            session_id: The session identifier
            properties: Dict of session properties to update
        """
        return tools.update(session_id, properties)

    @mcp.tool()
    def sessions_batch_delete(session_ids: list[str]) -> dict:
        """Batch delete multiple sessions.

        Args:
            session_ids: List of session IDs to delete
        """
        return tools.batch_delete(session_ids)

    @mcp.tool()
    def sessions_get_config(session_id: str) -> dict:
        """Get the configuration of a session.

        Args:
            session_id: The session identifier
        """
        return tools.get_config(session_id)

    @mcp.tool()
    def sessions_save_config(session_id: str) -> dict:
        """Save session configuration persistently.

        Args:
            session_id: The session identifier
        """
        return tools.save_config(session_id)

    @mcp.tool()
    def sessions_load_config(session_id: str, config_url: str) -> dict:
        """Load a configuration into a session.

        Args:
            session_id: The session identifier
            config_url: URL or path of the configuration to load
        """
        return tools.load_config(session_id, config_url)

    @mcp.tool()
    def sessions_get_meta(session_id: str) -> dict:
        """Get session metadata.

        Args:
            session_id: The session identifier
        """
        return tools.get_meta(session_id)

    @mcp.tool()
    def sessions_get_test(session_id: str) -> dict:
        """Get session test info (status, progress, etc.).

        Args:
            session_id: The session identifier
        """
        return tools.get_test(session_id)

    @mcp.tool()
    def sessions_touch(session_id: str) -> dict:
        """Keep a session alive (heartbeat).

        Args:
            session_id: The session identifier
        """
        return tools.touch(session_id)

    @mcp.tool()
    def sessions_add_applications(session_id: str, app_ids: list[str]) -> dict:
        """Add applications to a session's traffic profile.

        Args:
            session_id: The session identifier
            app_ids: List of application IDs to add
        """
        return tools.add_applications(session_id, app_ids)

    @mcp.tool()
    def sessions_test_init(session_id: str) -> dict:
        """Initialize a test for a session.

        Args:
            session_id: The session identifier
        """
        return tools.test_init(session_id)

    @mcp.tool()
    def sessions_test_end(session_id: str) -> dict:
        """End a test for a session.

        Args:
            session_id: The session identifier
        """
        return tools.test_end(session_id)

    @mcp.tool()
    def sessions_prepare_test(session_id: str) -> dict:
        """Prepare a test for a session (pre-flight checks).

        Args:
            session_id: The session identifier
        """
        return tools.prepare_test(session_id)
