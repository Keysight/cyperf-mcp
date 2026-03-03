from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, poll_async_operation


class NotificationTools:
    """Notification tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.NotificationsApi:
        return self._client.notifications

    def list(self, take=None, skip=None):
        try:
            kwargs = {}
            if take is not None:
                kwargs["take"] = take
            if skip is not None:
                kwargs["skip"] = skip
            result = self.api.get_notifications(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get(self, notification_id: str):
        try:
            result = self.api.get_notification_by_id(notification_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete(self, notification_id: str):
        try:
            self.api.delete_notification(notification_id)
            return {"result": f"Notification {notification_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def dismiss(self):
        try:
            result = self.api.start_notifications_dismiss()
            return poll_async_operation(result, self.api.poll_notifications_dismiss)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def cleanup(self):
        try:
            result = self.api.start_notifications_cleanup()
            return poll_async_operation(result, self.api.poll_notifications_cleanup)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_counts(self):
        try:
            result = self.api.get_notification_counts()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all notification tools with the MCP server."""
    tools = NotificationTools(client)

    @mcp.tool()
    def notifications_list(take: int = None, skip: int = None) -> dict:
        """List notifications.

        Args:
            take: Number of results to return
            skip: Number of results to skip
        """
        return tools.list(take, skip)

    @mcp.tool()
    def notifications_get(notification_id: str) -> dict:
        """Get notification details by ID.

        Args:
            notification_id: The notification identifier
        """
        return tools.get(notification_id)

    @mcp.tool()
    def notifications_delete(notification_id: str) -> dict:
        """Delete a notification.

        Args:
            notification_id: The notification identifier to delete
        """
        return tools.delete(notification_id)

    @mcp.tool()
    def notifications_dismiss() -> dict:
        """Dismiss all notifications."""
        return tools.dismiss()

    @mcp.tool()
    def notifications_cleanup() -> dict:
        """Clean up old notifications."""
        return tools.cleanup()

    @mcp.tool()
    def notifications_get_counts() -> dict:
        """Get notification counts by type/severity."""
        return tools.get_counts()
