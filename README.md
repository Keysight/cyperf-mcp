# CyPerf MCP Server

An [MCP](https://modelcontextprotocol.io/) (Model Context Protocol) server that exposes [Keysight CyPerf](https://www.keysight.com/us/en/products/network-test/protocol-load-test/cyperf.html) network performance and security testing functionality as **140 fine-grained tools** across 15 categories.

AI assistants connected via MCP can orchestrate CyPerf tests, manage agents, analyze results, and perform security testing — all through natural language.

## Quick Start

### Prerequisites

- Python 3.10+
- Access to a CyPerf controller

### Installation

```bash
# Clone the repository
git clone <repo-url> && cd cyperf-mcp

# Create a virtual environment and install
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Configuration

Create `~/.cyperf/config.json` with your controller connection details. You can override the path with the `CYPERF_CONFIG` environment variable.

**Multi-profile format** (recommended):

```json
{
  "default_profile": "lab1",
  "profiles": {
    "lab1": {
      "host": "https://10.36.75.100",
      "refresh_token": "eyJhbGciOi...",
      "verify_ssl": false
    },
    "cloud": {
      "host": "https://cyperf-cloud.example.com",
      "username": "admin",
      "password": "secret",
      "verify_ssl": true
    }
  }
}
```

**Single-profile shorthand**:

```json
{
  "host": "https://10.36.75.100",
  "refresh_token": "eyJhbGciOi...",
  "verify_ssl": false
}
```

Each profile requires:
- `host` — CyPerf controller URL
- Authentication — either `refresh_token` or `username` + `password`
- `verify_ssl` (optional, defaults to `true`)

### Running

**Stdio transport** (for AI assistant integration):
```bash
cyperf-mcp
```

**MCP Inspector** (interactive testing):
```bash
mcp dev src/cyperf_mcp/cyperf_mcp_server.py
```

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cyperf": {
      "command": "/path/to/your/.venv/bin/cyperf-mcp"
    }
  }
}
```

### Claude Code Integration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "cyperf": {
      "command": "/path/to/your/.venv/bin/cyperf-mcp"
    }
  }
}
```

## Architecture

```
src/cyperf_mcp/
├── cyperf_mcp_server.py   # FastMCP server entry point (stdio transport)
├── config.py              # Config file loader (~/.cyperf/config.json)
├── client.py              # CyPerf API client manager (lazy singleton)
├── helpers.py             # Serialization, error handling, async polling
└── tools/
    ├── __init__.py        # Tool registration aggregator
    ├── agents.py          # Agent management (11 tools)
    ├── sessions.py        # Session & config management (28 tools)
    ├── configs.py         # Configuration management (9 tools)
    ├── test_ops.py        # Test execution (7 tools)
    ├── results.py         # Results and reporting (8 tools)
    ├── resources.py       # Apps, attacks, TLS, captures (19 tools)
    ├── controllers.py     # Controller and port management (10 tools)
    ├── brokers.py         # Broker management (5 tools)
    ├── licensing.py       # License management (17 tools)
    ├── diagnostics.py     # Diagnostics export/cleanup (3 tools)
    ├── notifications.py   # Notification management (6 tools)
    ├── statistics.py      # Statistics plugins (4 tools)
    ├── certificates.py    # Certificate management (3 tools)
    ├── system.py          # System utilities (8 tools)
    └── migration.py       # Data migration (2 tools)
```

The server wraps the [`cyperf`](https://pypi.org/project/cyperf/) Python SDK's API classes directly. Each tool module follows a class-based pattern where a `*Tools` class holds the API logic, and a `register()` function wires `@mcp.tool()` decorated functions to those methods. Session config manipulation uses the SDK's DynamicModel pattern for in-place updates.

## Tool Catalog (140 tools)

All tools use `category_action` naming. Parameters with `= None` are optional.

### Sessions — 28 tools

Manage test sessions, traffic/attack profiles, network segments, and test objectives.

| Tool | Description |
|---|---|
| `sessions_list` | List all sessions with optional search/filter |
| `sessions_create` | Create a new session |
| `sessions_get` | Get session details by ID |
| `sessions_delete` | Delete one or more sessions (stops running tests first) |
| `sessions_update` | Update session properties |
| `sessions_get_config` | Get session configuration |
| `sessions_save_config` | Save session config (optionally with a new name) |
| `sessions_load_config` | Load a config into session |
| `sessions_get_meta` | Get session metadata |
| `sessions_get_test` | Get session test info (status, progress) |
| `sessions_touch` | Keep session alive (heartbeat) |
| `sessions_add_applications` | Add applications by name to a traffic profile |
| `sessions_add_attacks` | Add attacks by name to an attack profile |
| `sessions_get_applications` | List applications in a traffic profile |
| `sessions_get_attacks` | List attacks in an attack profile |
| `sessions_get_app_actions` | List actions and params for an application |
| `sessions_set_app_action_param` | Set an action parameter value |
| `sessions_remove_app_action` | Remove an action from an application |
| `sessions_remove_application` | Remove an application from a traffic profile |
| `sessions_remove_attack` | Remove an attack from an attack profile |
| `sessions_delete_traffic_profile` | Delete a traffic/application profile |
| `sessions_delete_attack_profile` | Delete an attack profile |
| `sessions_assign_agents` | Assign agents to named network segments |
| `sessions_rename_network_segments` | Rename network segments |
| `sessions_get_network_segments` | List network segments with IP range details |
| `sessions_set_network_ip_range` | Update IP range properties on a segment |
| `sessions_disable_automatic_network` | Disable automatic IP on all segments |
| `sessions_set_objective_and_timeline` | Set test objective type, value, and duration |

### Agents — 11 tools

Manage CyPerf test agents (virtual or hardware appliances).

| Tool | Description |
|---|---|
| `agents_list` | List all agents with optional search/filter |
| `agents_get` | Get agent details by ID |
| `agents_delete` | Delete one or more agents |
| `agents_update` | Update agent properties |
| `agents_reserve` | Reserve agents for testing |
| `agents_release` | Release reserved agents |
| `agents_reboot` | Reboot agents |
| `agents_set_dpdk` | Set DPDK mode on agents |
| `agents_set_ntp` | Set NTP configuration on agents |
| `agents_tags` | List agent tags |
| `agents_export_files` | Export agent files (logs, configs) |

### Configurations — 9 tools

Manage saved test configurations (templates).

| Tool | Description |
|---|---|
| `configs_list` | List configurations with optional search/filter |
| `configs_get` | Get configuration by ID |
| `configs_create` | Create a new configuration |
| `configs_delete` | Delete one or more configurations |
| `configs_update` | Update configuration metadata |
| `configs_import` | Import a configuration file |
| `configs_import_all` | Import all configurations from file |
| `configs_export_all` | Export configurations |
| `configs_categories` | List configuration categories |

### Test Operations — 7 tools

Control test execution lifecycle.

| Tool | Description |
|---|---|
| `test_start` | Start a test run (polls until running) |
| `test_stop` | Stop a running test gracefully |
| `test_abort` | Abort a test run immediately |
| `test_calibrate` | Start or stop test calibration |
| `test_init` | Initialize test (allocate resources) |
| `test_end` | End test and release resources |
| `test_prepare` | Prepare test (pre-flight validation) |

### Results — 8 tools

Access and export test results, statistics, and reports.

| Tool | Description |
|---|---|
| `results_list` | List test results with optional search/filter |
| `results_get` | Get result details by ID |
| `results_delete` | Delete one or more results |
| `results_stats` | List all stats, or get a specific stat (latest snapshot as compact table) |
| `results_files` | List all files, or get a specific file by ID |
| `results_download_config` | Download result configuration |
| `results_generate_report` | Generate report (csv, pdf, or all) |
| `results_tags` | List result tags |

### Resources — 19 tools

Browse and search application resources, attacks, TLS certificates, captures, and more.

| Tool | Description |
|---|---|
| `resources_list_apps` | List applications with optional search/filter |
| `resources_get_app` | Get application details |
| `resources_list_app_types` | List application types |
| `resources_list_attacks` | List attacks/strikes with optional search/filter |
| `resources_get_attack` | Get attack details |
| `resources_list_attack_categories` | List attack categories |
| `resources_list_auth_profiles` | List authentication profiles |
| `resources_list_captures` | List packet captures |
| `resources_get_capture` | Get capture details |
| `resources_delete_capture` | Delete a packet capture |
| `resources_list_tls_certs` | List TLS certificates |
| `resources_get_tls_cert` | Get TLS certificate details |
| `resources_delete_tls_cert` | Delete a TLS certificate |
| `resources_list_custom_fuzzing` | List custom fuzzing scripts |
| `resources_list_payloads` | List payloads |
| `resources_list_pcaps` | List PCAP files |
| `resources_list_http_profiles` | List HTTP profiles |
| `resources_search_apps` | Search apps by substring (name or description) |
| `resources_search_attacks` | Search attacks by substring (name or description) |

### Controllers — 10 tools

Manage CyPerf controllers, compute nodes, and ports.

| Tool | Description |
|---|---|
| `controllers_list` | List controllers |
| `controllers_get` | Get controller details |
| `controllers_nodes` | List compute nodes, or get one by ID |
| `controllers_ports` | List ports, or get one by ID |
| `controllers_set_app` | Set application on controller |
| `controllers_clear_ports` | Clear port ownership |
| `controllers_power_cycle` | Power cycle compute nodes |
| `controllers_reboot_port` | Reboot a port |
| `controllers_set_link_state` | Set port link state (up/down) |
| `controllers_set_aggregation` | Set node aggregation mode |

### Brokers — 5 tools

Manage network brokers.

| Tool | Description |
|---|---|
| `brokers_list` | List brokers |
| `brokers_create` | Create a broker |
| `brokers_get` | Get broker details |
| `brokers_update` | Update broker properties |
| `brokers_delete` | Delete a broker |

### Licensing — 17 tools

Manage licenses and license servers.

| Tool | Description |
|---|---|
| `licensing_list_licenses` | List all installed licenses |
| `licensing_get_license` | Get license details |
| `licensing_activate` | Activate a license |
| `licensing_deactivate` | Deactivate a license |
| `licensing_sync` | Synchronize licenses |
| `licensing_get_hostid` | Get host ID |
| `licensing_reserve_feature` | Reserve a license feature |
| `licensing_remove_reservation` | Remove a reservation |
| `licensing_test_connectivity` | Test backend connectivity |
| `licensing_get_activation_info` | Get activation code info |
| `licensing_get_entitlement_info` | Get entitlement code info |
| `licensing_get_feature_stats` | Get feature statistics |
| `licensing_list_servers` | List license servers |
| `licensing_add_server` | Add a license server |
| `licensing_get_server` | Get license server details |
| `licensing_update_server` | Update license server |
| `licensing_delete_server` | Delete license server |

### Diagnostics — 3 tools

Export and manage diagnostic data.

| Tool | Description |
|---|---|
| `diagnostics_list_components` | List diagnostic components |
| `diagnostics_export` | Export diagnostics |
| `diagnostics_delete` | Delete diagnostics data |

### Notifications — 6 tools

Manage system notifications.

| Tool | Description |
|---|---|
| `notifications_list` | List notifications |
| `notifications_get` | Get notification details |
| `notifications_delete` | Delete a notification |
| `notifications_dismiss` | Dismiss all notifications |
| `notifications_cleanup` | Clean up old notifications |
| `notifications_get_counts` | Get notification counts |

### Statistics — 4 tools

Manage statistics plugins for external ingestion.

| Tool | Description |
|---|---|
| `stats_list_plugins` | List stats plugins |
| `stats_create_plugin` | Create a stats plugin |
| `stats_delete_plugin` | Delete a stats plugin |
| `stats_ingest` | Ingest external statistics |

### Certificates — 3 tools

Manage controller certificates.

| Tool | Description |
|---|---|
| `certs_list` | List certificates |
| `certs_generate` | Generate a certificate |
| `certs_upload` | Upload a certificate |

### System — 8 tools

System utilities: time, disk, EULA, logging.

| Tool | Description |
|---|---|
| `system_get_time` | Get server time |
| `system_get_disk_usage` | Get disk usage overview |
| `system_list_disk_consumers` | List disk consumers |
| `system_cleanup` | Clean up disk space (diagnostics, logs, or results) |
| `system_check_eula` | Check EULA acceptance |
| `system_accept_eula` | Accept EULA |
| `system_get_log_config` | Get logging config |
| `system_set_log_config` | Set logging config |

### Migration — 2 tools

Export and import controller data for migration.

| Tool | Description |
|---|---|
| `migration_export` | Export controller data |
| `migration_import` | Import controller data |

## Example Workflows

### Run a Performance Test

```
1. sessions_create  session_data={...}                → create a new session
2. sessions_load_config  session_id, config_url       → load a test config
3. agents_list  exclude_offline='true'                → find available agents
4. sessions_assign_agents  session_id,
     agent_assignments={"Client": [...], "Server": [...]}  → assign agents
5. sessions_set_objective_and_timeline  session_id,
     objective_type="SIMULATED_USERS", objective_value=100, duration=600
6. test_init  session_id                              → initialize the test
7. test_start  session_id                             → start the test run
8. sessions_get_test  session_id                      → check test status
9. test_stop  session_id                              → stop when done
10. results_list                                      → find the result
11. results_stats  result_id                          → view statistics
12. results_generate_report  result_id, format="pdf"  → generate PDF report
```

### Add Applications to a Session

```
1. resources_search_apps  query="HTTP"                → find apps by name
2. sessions_add_applications  session_id,
     traffic_profile_id="1", app_names=["HTTP"]       → add apps by name
3. sessions_get_applications  session_id              → verify apps added
4. sessions_get_app_actions  session_id, app_id=...   → inspect app actions/params
5. sessions_set_app_action_param  session_id,
     app_id=..., action_id=..., param_id=..., value="..."  → configure params
```

### Security Assessment

```
1. resources_search_attacks  query="CVE-2024"         → find attacks by name
2. sessions_create  session_data={...}                → create session
3. sessions_add_attacks  session_id,
     attack_profile_id="1", attack_names=[...]        → add attacks by name
4. sessions_assign_agents  session_id, agent_assignments={...}
5. test_start  session_id                             → run the security test
6. results_stats  result_id                           → analyze results
```

### Infrastructure Management

```
1. controllers_list                                   → list controllers
2. controllers_nodes  controller_id                   → inspect compute nodes
3. agents_list                                        → view all agents
4. agents_reserve  agent_ids=[...]                    → reserve agents
5. system_get_disk_usage                              → check disk space
6. system_cleanup  target="results"                   → free disk space
7. licensing_list_licenses                            → check license status
```

## Error Handling

All tools return structured JSON responses. On success, you get the API response data. On failure:

```json
{
  "error": true,
  "status": 404,
  "reason": "Not Found",
  "message": "Resource not found"
}
```

Async operations (test start/stop, batch deletes, exports) use the SDK's built-in `await_completion()` for polling. A manual `poll_async_operation` fallback is available with a default timeout of 300 seconds.

## Development

```bash
# Install in development mode
pip install -e .

# Run with MCP Inspector for interactive testing
mcp dev src/cyperf_mcp/cyperf_mcp_server.py
```

## License

Proprietary — Keysight Technologies.
