# CyPerf MCP Server — Tool Reference

Complete reference for all 140 tools. Parameters marked with `= None` are optional.

Back to [README](../README.md).

---

## Table of Contents

- [Agents (12 tools)](#agents--12-tools)
- [Sessions (16 tools)](#sessions--16-tools)
- [Configurations (10 tools)](#configurations--10-tools)
- [Test Operations (8 tools)](#test-operations--8-tools)
- [Results (13 tools)](#results--13-tools)
- [Resources (17 tools)](#resources--17-tools)
- [Controllers (12 tools)](#controllers--12-tools)
- [Brokers (5 tools)](#brokers--5-tools)
- [Licensing (17 tools)](#licensing--17-tools)
- [Diagnostics (3 tools)](#diagnostics--3-tools)
- [Notifications (6 tools)](#notifications--6-tools)
- [Statistics (6 tools)](#statistics--6-tools)
- [Certificates (3 tools)](#certificates--3-tools)
- [System (10 tools)](#system--10-tools)
- [Migration (2 tools)](#migration--2-tools)

---

## Agents — 12 tools

Manage CyPerf test agents (virtual or hardware appliances that generate and receive traffic).

Source: [`tools/agents.py`](../src/cyperf_mcp/tools/agents.py) | CyPerf API: `AgentsApi`

### `agents_list`

List all CyPerf agents with optional filtering.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |
| `exclude_offline` | string | No | Set to `"true"` to exclude offline agents |

### `agents_get`

Get details of a specific CyPerf agent by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_id` | string | Yes | The agent identifier |

### `agents_delete`

Delete a CyPerf agent.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_id` | string | Yes | The agent identifier to delete |

### `agents_update`

Update agent properties.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_id` | string | Yes | The agent identifier |
| `properties` | object | Yes | Dict of agent properties to update (e.g. `name`, `tags`) |

### `agents_batch_delete`

Batch delete multiple agents. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_ids` | list[string] | Yes | List of agent IDs to delete |

### `agents_reserve`

Reserve agents for testing. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_ids` | list[string] | Yes | List of agent IDs to reserve |

### `agents_release`

Release reserved agents. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_ids` | list[string] | Yes | List of agent IDs to release |

### `agents_reboot`

Reboot agents. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_ids` | list[string] | Yes | List of agent IDs to reboot |

### `agents_set_dpdk`

Set DPDK mode on agents. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_ids` | list[string] | Yes | List of agent IDs |
| `enabled` | boolean | Yes | Whether to enable DPDK mode |

### `agents_set_ntp`

Set NTP configuration on agents. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_ids` | list[string] | Yes | List of agent IDs |
| `ntp_server` | string | Yes | NTP server address |

### `agents_tags`

List agent tags.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `agents_export_files`

Export agent files (logs, configs, etc.). Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `agent_ids` | list[string] | Yes | List of agent IDs to export files from |
| `file_type` | string | No | Type of files to export |

---

## Sessions — 16 tools

Manage test sessions — the working context where you load configurations, assign agents, and run tests.

Source: [`tools/sessions.py`](../src/cyperf_mcp/tools/sessions.py) | CyPerf API: `SessionsApi`

### `sessions_list`

List all CyPerf sessions.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `sessions_create`

Create a new CyPerf session.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_data` | object | Yes | Session properties (e.g. `name`, `description`) |

### `sessions_get`

Get details of a specific session by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `sessions_delete`

Delete a session.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier to delete |

### `sessions_update`

Update session properties.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |
| `properties` | object | Yes | Dict of session properties to update |

### `sessions_batch_delete`

Batch delete multiple sessions. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_ids` | list[string] | Yes | List of session IDs to delete |

### `sessions_get_config`

Get the configuration of a session.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `sessions_save_config`

Save session configuration persistently. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `sessions_load_config`

Load a configuration into a session. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |
| `config_url` | string | Yes | URL or path of the configuration to load |

### `sessions_get_meta`

Get session metadata.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `sessions_get_test`

Get session test info (status, progress, etc.).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `sessions_touch`

Keep a session alive (heartbeat). Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `sessions_add_applications`

Add applications to a session's traffic profile. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |
| `app_ids` | list[string] | Yes | List of application IDs to add |

### `sessions_test_init`

Initialize a test for a session. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `sessions_test_end`

End a test for a session. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `sessions_prepare_test`

Prepare a test for a session (pre-flight checks). Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

---

## Configurations — 10 tools

Manage saved test configurations (reusable templates).

Source: [`tools/configs.py`](../src/cyperf_mcp/tools/configs.py) | CyPerf API: `ConfigurationsApi`

### `configs_list`

List available CyPerf configurations.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `configs_get`

Get a configuration by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `config_id` | string | Yes | The configuration identifier |

### `configs_create`

Create a new configuration.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `config_data` | object | Yes | Configuration properties (`name`, `description`, etc.) |

### `configs_delete`

Delete a configuration.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `config_id` | string | Yes | The configuration identifier to delete |

### `configs_update`

Update configuration metadata.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `config_id` | string | Yes | The configuration identifier |
| `properties` | object | Yes | Dict of properties to update |

### `configs_batch_delete`

Batch delete multiple configurations. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `config_ids` | list[string] | Yes | List of configuration IDs to delete |

### `configs_import`

Import a configuration from a local file. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `file_path` | string | Yes | Path to the configuration file to import |

### `configs_import_all`

Import all configurations from a file. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `file_path` | string | Yes | Path to the file containing configurations |

### `configs_export_all`

Export configurations. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `config_ids` | list[string] | No | Optional list of configuration IDs to export (all if omitted) |

### `configs_categories`

List configuration categories.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

---

## Test Operations — 8 tools

Control the test execution lifecycle: init, start, stop, abort, calibrate.

Source: [`tools/test_ops.py`](../src/cyperf_mcp/tools/test_ops.py) | CyPerf API: `TestOperationsApi`, `SessionsApi`

All test operations poll their async operation to completion.

### `test_start`

Start a test run for a session.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `test_stop`

Stop a running test gracefully.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `test_abort`

Abort a test run immediately.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `test_calibrate_start`

Start test calibration.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `test_calibrate_stop`

Stop test calibration.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `test_init`

Initialize a test (allocate resources, prepare agents).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `test_end`

End a test and release resources.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

### `test_prepare`

Prepare a test (pre-flight validation and setup).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | The session identifier |

---

## Results — 13 tools

Access test results, statistics, files, and generate reports.

Source: [`tools/results.py`](../src/cyperf_mcp/tools/results.py) | CyPerf API: `TestResultsApi`, `ReportsApi`

### `results_list`

List test results.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `results_get`

Get test result details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |

### `results_delete`

Delete a test result.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier to delete |

### `results_batch_delete`

Batch delete multiple test results. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_ids` | list[string] | Yes | List of result IDs to delete |

### `results_get_stats`

Get statistics for a test result.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |
| `take` | integer | No | Number of stats to return |
| `skip` | integer | No | Number of stats to skip |

### `results_get_stat`

Get a specific statistic by ID from a test result.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |
| `stat_id` | string | Yes | The statistic identifier |

### `results_get_files`

List files associated with a test result.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |
| `take` | integer | No | Number of files to return |
| `skip` | integer | No | Number of files to skip |

### `results_get_file`

Get a specific result file metadata.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |
| `file_id` | string | Yes | The file identifier |

### `results_download_config`

Download the configuration used for a test result.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |

### `results_generate_csv`

Generate a CSV report for a test result. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |

### `results_generate_pdf`

Generate a PDF report for a test result. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |

### `results_generate_all`

Generate all report formats (CSV + PDF) for a test result. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The result identifier |

### `results_tags`

List result tags.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of tags to return |
| `skip` | integer | No | Number of tags to skip |

---

## Resources — 17 tools

Browse and manage application resources: apps, attacks/strikes, TLS certificates, captures, fuzzing scripts, and more.

Source: [`tools/resources.py`](../src/cyperf_mcp/tools/resources.py) | CyPerf API: `ApplicationResourcesApi`

### `resources_list_apps`

List available applications for traffic generation.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_get_app`

Get application details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `app_id` | string | Yes | The application identifier |

### `resources_list_app_types`

List application types (HTTP, TLS, etc.).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_list_attacks`

List available attacks/strikes for security testing.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_get_attack`

Get attack/strike details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `attack_id` | string | Yes | The attack identifier |

### `resources_list_attack_categories`

List attack categories.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_list_auth_profiles`

List authentication profiles.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_list_captures`

List packet captures.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_get_capture`

Get packet capture details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `capture_id` | string | Yes | The capture identifier |

### `resources_delete_capture`

Delete a packet capture.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `capture_id` | string | Yes | The capture identifier to delete |

### `resources_list_tls_certs`

List TLS certificates.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_get_tls_cert`

Get TLS certificate details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `cert_id` | string | Yes | The certificate identifier |

### `resources_delete_tls_cert`

Delete a TLS certificate.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `tls_cert_id` | string | Yes | The TLS certificate identifier to delete |

### `resources_list_custom_fuzzing`

List custom fuzzing scripts.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_list_payloads`

List payloads.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_list_pcaps`

List PCAP files.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `resources_list_http_profiles`

List HTTP profiles.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

---

## Controllers — 12 tools

Manage CyPerf controllers, their compute nodes, and network ports.

Source: [`tools/controllers.py`](../src/cyperf_mcp/tools/controllers.py) | CyPerf API: `AgentsApi` (controller endpoints)

### `controllers_list`

List all controllers.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `controllers_get`

Get controller details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |

### `controllers_list_nodes`

List compute nodes on a controller.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `controllers_get_node`

Get compute node details.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `node_id` | string | Yes | The compute node identifier |

### `controllers_list_ports`

List ports on a controller.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `controllers_get_port`

Get port details.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `port_id` | string | Yes | The port identifier |

### `controllers_set_app`

Set application on a controller. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `app_id` | string | Yes | The application identifier to set |

### `controllers_clear_ports`

Clear port ownership on a controller. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |

### `controllers_power_cycle`

Power cycle compute nodes. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `node_ids` | list[string] | Yes | List of node IDs to power cycle |

### `controllers_reboot_port`

Reboot a port on a controller. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `port_id` | string | Yes | The port identifier to reboot |

### `controllers_set_link_state`

Set port link state (up/down). Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `port_id` | string | Yes | The port identifier |
| `state` | string | Yes | The desired link state (e.g. `"up"`, `"down"`) |

### `controllers_set_aggregation`

Set node aggregation mode. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `controller_id` | string | Yes | The controller identifier |
| `node_id` | string | Yes | The compute node identifier |
| `mode` | string | Yes | The aggregation mode to set |

---

## Brokers — 5 tools

Manage network brokers.

Source: [`tools/brokers.py`](../src/cyperf_mcp/tools/brokers.py) | CyPerf API: `BrokersApi`

### `brokers_list`

List all brokers.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `brokers_create`

Create a new broker.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `broker_data` | object | Yes | Broker properties (e.g. `host`, `port`, `name`) |

### `brokers_get`

Get broker details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `broker_id` | string | Yes | The broker identifier |

### `brokers_update`

Update broker properties.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `broker_id` | string | Yes | The broker identifier |
| `properties` | object | Yes | Dict of broker properties to update |

### `brokers_delete`

Delete a broker.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `broker_id` | string | Yes | The broker identifier to delete |

---

## Licensing — 17 tools

Manage licenses, license servers, and feature reservations.

Source: [`tools/licensing.py`](../src/cyperf_mcp/tools/licensing.py) | CyPerf API: `LicensingApi`, `LicenseServersApi`

### `licensing_list_licenses`

List all installed licenses. No parameters.

### `licensing_get_license`

Get license details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `license_id` | integer | Yes | The license identifier |

### `licensing_activate`

Activate a license with an activation code.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `activation_code` | string | Yes | The activation code |

### `licensing_deactivate`

Deactivate a license.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `activation_code` | string | Yes | The activation code to deactivate |

### `licensing_sync`

Synchronize licenses with the license server. No parameters.

### `licensing_get_hostid`

Get the host ID for licensing. No parameters.

### `licensing_reserve_feature`

Reserve a license feature.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `license_id` | integer | Yes | The license identifier |
| `feature_name` | string | Yes | Name of the feature to reserve |
| `count` | integer | Yes | Number of units to reserve |

### `licensing_remove_reservation`

Remove a license reservation.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `license_id` | integer | Yes | The license identifier |

### `licensing_test_connectivity`

Test connectivity to the license backend server. No parameters.

### `licensing_get_activation_info`

Get information about an activation code.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `activation_code` | string | Yes | The activation code to look up |

### `licensing_get_entitlement_info`

Get information about an entitlement code.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `entitlement_code` | string | Yes | The entitlement code to look up |

### `licensing_get_feature_stats`

Get counted feature statistics for licenses. No parameters.

### `licensing_list_servers`

List license servers.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `licensing_add_server`

Add a license server.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `server_data` | object | Yes | License server properties (e.g. `host`, `port`) |

### `licensing_get_server`

Get license server details.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `server_id` | string | Yes | The license server identifier |

### `licensing_update_server`

Update license server properties.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `server_id` | string | Yes | The license server identifier |
| `properties` | object | Yes | Dict of properties to update |

### `licensing_delete_server`

Delete a license server.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `server_id` | string | Yes | The license server identifier to delete |

---

## Diagnostics — 3 tools

Export and manage diagnostic data from the CyPerf controller.

Source: [`tools/diagnostics.py`](../src/cyperf_mcp/tools/diagnostics.py) | CyPerf API: `DiagnosticsApi`

### `diagnostics_list_components`

List diagnostic components available for export. No parameters.

### `diagnostics_export`

Export diagnostics. Optionally filter by component names.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `component_names` | list[string] | No | Optional list of component names to export |

### `diagnostics_delete`

Delete all diagnostics data. No parameters.

---

## Notifications — 6 tools

Manage system notifications and alerts.

Source: [`tools/notifications.py`](../src/cyperf_mcp/tools/notifications.py) | CyPerf API: `NotificationsApi`

### `notifications_list`

List notifications.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `notifications_get`

Get notification details by ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `notification_id` | string | Yes | The notification identifier |

### `notifications_delete`

Delete a notification.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `notification_id` | string | Yes | The notification identifier to delete |

### `notifications_dismiss`

Dismiss all notifications. Polls async operation to completion. No parameters.

### `notifications_cleanup`

Clean up old notifications. Polls async operation to completion. No parameters.

### `notifications_get_counts`

Get notification counts by type/severity. No parameters.

---

## Statistics — 6 tools

Manage statistics plugins and query test result statistics.

Source: [`tools/statistics.py`](../src/cyperf_mcp/tools/statistics.py) | CyPerf API: `StatisticsApi`

### `stats_list_plugins`

List stats plugins.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `stats_create_plugin`

Create a stats plugin for external statistics ingestion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `plugin_data` | object | Yes | Plugin configuration (e.g. `name`, `type`, `endpoint`) |

### `stats_delete_plugin`

Delete a stats plugin.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `plugin_id` | string | Yes | The plugin identifier to delete |

### `stats_ingest`

Ingest external statistics via a plugin. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `operation_data` | object | Yes | Ingestion operation parameters |

### `stats_get_result_stats`

Get statistics for a test result.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The test result identifier |
| `take` | integer | No | Number of stats to return |
| `skip` | integer | No | Number of stats to skip |

### `stats_get_result_stat`

Get a specific statistic by name from a test result.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `result_id` | string | Yes | The test result identifier |
| `stat_id` | string | Yes | The statistic name/identifier |

---

## Certificates — 3 tools

Manage controller certificates via the cert manager.

Source: [`tools/certificates.py`](../src/cyperf_mcp/tools/certificates.py) | CyPerf API: `UtilsApi`

### `certs_list`

List certificates managed by the cert manager. No parameters.

### `certs_generate`

Generate a new certificate. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `cert_data` | object | Yes | Certificate properties (e.g. `common_name`, `organization`, `validity`) |

### `certs_upload`

Upload a certificate to the cert manager. Polls async operation to completion. No parameters.

---

## System — 10 tools

System utilities: server time, disk usage, EULA, logging configuration.

Source: [`tools/system.py`](../src/cyperf_mcp/tools/system.py) | CyPerf API: `UtilsApi`

### `system_get_time`

Get the CyPerf server time. No parameters.

### `system_get_disk_usage`

Get disk usage overview for the CyPerf controller. No parameters.

### `system_list_disk_consumers`

List disk usage consumers (what's using disk space).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `take` | integer | No | Number of results to return |
| `skip` | integer | No | Number of results to skip |

### `system_cleanup_diagnostics`

Clean up diagnostics data to free disk space. Polls async operation to completion. No parameters.

### `system_cleanup_logs`

Clean up log files to free disk space. Polls async operation to completion. No parameters.

### `system_cleanup_results`

Clean up old test results to free disk space. Polls async operation to completion. No parameters.

### `system_check_eula`

Check EULA acceptance status. No parameters.

### `system_accept_eula`

Accept the End User License Agreement. No parameters.

### `system_get_log_config`

Get the current logging configuration. No parameters.

### `system_set_log_config`

Set logging configuration.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `config_data` | object | Yes | Logging configuration (e.g. `level`, file settings) |

---

## Migration — 2 tools

Export and import controller data for migration between CyPerf instances.

Source: [`tools/migration.py`](../src/cyperf_mcp/tools/migration.py) | CyPerf API: `DataMigrationApi`

### `migration_export`

Export controller data for migration. Polls async operation to completion.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `export_data` | object | No | Optional export parameters (e.g. filter criteria) |

### `migration_import`

Import controller data from a migration package. Polls async operation to completion. No parameters.
