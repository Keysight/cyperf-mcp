from __future__ import annotations

import cyperf
from .config import CyPerfConfig


class CyPerfClientManager:
    """Manages lazy-initialized cyperf API client and API class instances."""

    def __init__(self, config: CyPerfConfig, profile_name: str | None = None):
        self._config = config
        self._profile_name = profile_name
        self._api_client: cyperf.ApiClient | None = None

    @property
    def api_client(self) -> cyperf.ApiClient:
        if self._api_client is None:
            profile = self._config.get_profile(self._profile_name)
            cfg = cyperf.Configuration(host=profile["host"])
            cfg.verify_ssl = profile.get("verify_ssl", True)

            if "refresh_token" in profile:
                cfg.refresh_token = profile["refresh_token"]
            elif "username" in profile:
                cfg.username = profile["username"]
                cfg.password = profile["password"]

            self._api_client = cyperf.ApiClient(cfg)
        return self._api_client

    @property
    def agents(self) -> cyperf.AgentsApi:
        return cyperf.AgentsApi(self.api_client)

    @property
    def sessions(self) -> cyperf.SessionsApi:
        return cyperf.SessionsApi(self.api_client)

    @property
    def configs(self) -> cyperf.ConfigurationsApi:
        return cyperf.ConfigurationsApi(self.api_client)

    @property
    def test_ops(self) -> cyperf.TestOperationsApi:
        return cyperf.TestOperationsApi(self.api_client)

    @property
    def results(self) -> cyperf.TestResultsApi:
        return cyperf.TestResultsApi(self.api_client)

    @property
    def resources(self) -> cyperf.ApplicationResourcesApi:
        return cyperf.ApplicationResourcesApi(self.api_client)

    @property
    def licensing(self) -> cyperf.LicensingApi:
        return cyperf.LicensingApi(self.api_client)

    @property
    def license_servers(self) -> cyperf.LicenseServersApi:
        return cyperf.LicenseServersApi(self.api_client)

    @property
    def brokers(self) -> cyperf.BrokersApi:
        return cyperf.BrokersApi(self.api_client)

    @property
    def controllers(self) -> cyperf.AgentsApi:
        return cyperf.AgentsApi(self.api_client)

    @property
    def diagnostics(self) -> cyperf.DiagnosticsApi:
        return cyperf.DiagnosticsApi(self.api_client)

    @property
    def statistics(self) -> cyperf.StatisticsApi:
        return cyperf.StatisticsApi(self.api_client)

    @property
    def notifications(self) -> cyperf.NotificationsApi:
        return cyperf.NotificationsApi(self.api_client)

    @property
    def reports(self) -> cyperf.ReportsApi:
        return cyperf.ReportsApi(self.api_client)

    @property
    def migration(self) -> cyperf.DataMigrationApi:
        return cyperf.DataMigrationApi(self.api_client)

    @property
    def utils(self) -> cyperf.UtilsApi:
        return cyperf.UtilsApi(self.api_client)

    @property
    def auth(self) -> cyperf.AuthorizationApi:
        return cyperf.AuthorizationApi(self.api_client)
