from __future__ import annotations

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, poll_async_operation


class CertificateTools:
    """Certificate management tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.UtilsApi:
        return self._client.utils

    def list(self):
        try:
            result = self.api.get_cert_manager_certificate()
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def generate(self, cert_data: dict):
        try:
            # Map user-friendly names to Certificate model fields
            mapped = {}
            if "common_name" in cert_data:
                mapped["dns_names"] = [cert_data.pop("common_name")]
            mapped.update(cert_data)
            cert = cyperf.Certificate(**mapped)
            result = self.api.start_cert_manager_generate(certificate=cert)
            try:
                return poll_async_operation(result, self.api.poll_cert_manager_generate)
            except cyperf.ApiException:
                return {"result": "certificate generation initiated", "operation_id": result.id}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def upload(self):
        try:
            result = self.api.start_cert_manager_upload()
            return poll_async_operation(result, self.api.poll_cert_manager_upload)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all certificate tools with the MCP server."""
    tools = CertificateTools(client)

    @mcp.tool()
    def certs_list() -> dict:
        """[Certificates] List certificates managed by the cert manager."""
        return tools.list()

    @mcp.tool()
    def certs_generate(cert_data: dict) -> dict:
        """[Certificates] Generate a new certificate.

        Args:
            cert_data: Certificate properties (e.g. common_name, organization, validity)
        """
        return tools.generate(cert_data)

    @mcp.tool()
    def certs_upload() -> dict:
        """[Certificates] Upload a certificate to the cert manager."""
        return tools.upload()
