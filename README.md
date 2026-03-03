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
    ├── agents.py          # Agent management (12 tools)
    ├── sessions.py        # Session management (16 tools)
    ├── configs.py         # Configuration management (10 tools)
    ├── test_ops.py        # Test execution (8 tools)
    ├── results.py         # Results and reporting (13 tools)
    ├── resources.py       # Apps, attacks, TLS, captures (17 tools)
    ├── controllers.py     # Controller and port management (12 tools)
    ├── brokers.py         # Broker management (5 tools)
    ├── licensing.py       # License management (17 tools)
    ├── diagnostics.py     # Diagnostics export/cleanup (3 tools)
    ├── notifications.py   # Notification management (6 tools)
    ├── statistics.py      # Statistics and plugins (6 tools)
    ├── certificates.py    # Certificate management (3 tools)
    ├── system.py          # System utilities (10 tools)
    └── migration.py       # Data migration (2 tools)
```

The server wraps the [`cyperf`](https://pypi.org/project/cyperf/) Python SDK's API classes directly. Each tool module follows a class-based pattern where a `*Tools` class holds the API logic, and a `register()` function wires `@mcp.tool()` decorated functions to those methods.

## Tool Catalog (140 tools)

All tools use `category_action` naming. Parameters with `= None` are optional.

For the complete reference with parameter details, see **[docs/tools.md](docs/tools.md)**.

### Agents — 12 tools

Manage CyPerf test agents (virtual or hardware appliances).

| Tool | Description |
|---|---|
| `agents_list` | List all agents with optional filtering |
| `agents_get` | Get agent details by ID |
| `agents_delete` | Delete an agent |
| `agents_update` | Update agent properties |
| `agents_batch_delete` | Batch delete multiple agents |
| `agents_reserve` | Reserve agents for testing |
| `agents_release` | Release reserved agents |
| `agents_reboot` | Reboot agents |
| `agents_set_dpdk` | Set DPDK mode on agents |
| `agents_set_ntp` | Set NTP configuration on agents |
| `agents_tags` | List agent tags |
| `agents_export_files` | Export agent files (logs, configs) |

### Sessions — 16 tools

Manage test sessions — the working context for test configuration and execution.

| Tool | Description |
|---|---|
| `sessions_list` | List all sessions |
| `sessions_create` | Create a new session |
| `sessions_get` | Get session details by ID |
| `sessions_delete` | Delete a session |
| `sessions_update` | Update session properties |
| `sessions_batch_delete` | Batch delete multiple sessions |
| `sessions_get_config` | Get session configuration |
| `sessions_save_config` | Save session config persistently |
| `sessions_load_config` | Load a config into session |
| `sessions_get_meta` | Get session metadata |
| `sessions_get_test` | Get session test info (status, progress) |
| `sessions_touch` | Keep session alive (heartbeat) |
| `sessions_add_applications` | Add applications to traffic profile |
| `sessions_test_init` | Initialize a test for a session |
| `sessions_test_end` | End a test for a session |
| `sessions_prepare_test` | Prepare a test (pre-flight checks) |

### Configurations — 10 tools

Manage saved test configurations (templates).

| Tool | Description |
|---|---|
| `configs_list` | List available configurations |
| `configs_get` | Get configuration by ID |
| `configs_create` | Create a new configuration |
| `configs_delete` | Delete a configuration |
| `configs_update` | Update configuration metadata |
| `configs_batch_delete` | Batch delete configurations |
| `configs_import` | Import a configuration file |
| `configs_import_all` | Import all configurations from file |
| `configs_export_all` | Export configurations |
| `configs_categories` | List configuration categories |

### Test Operations — 8 tools

Control test execution lifecycle.

| Tool | Description |
|---|---|
| `test_start` | Start a test run (polls until running) |
| `test_stop` | Stop a running test gracefully |
| `test_abort` | Abort a test run immediately |
| `test_calibrate_start` | Start test calibration |
| `test_calibrate_stop` | Stop test calibration |
| `test_init` | Initialize test (allocate resources) |
| `test_end` | End test and release resources |
| `test_prepare` | Prepare test (pre-flight validation) |

### Results — 13 tools

Access and export test results, statistics, and reports.

| Tool | Description |
|---|---|
| `results_list` | List test results |
| `results_get` | Get result details by ID |
| `results_delete` | Delete a result |
| `results_batch_delete` | Batch delete results |
| `results_get_stats` | Get result statistics |
| `results_get_stat` | Get a specific statistic by ID |
| `results_get_files` | List result files |
| `results_get_file` | Get a specific result file |
| `results_download_config` | Download result configuration |
| `results_generate_csv` | Generate CSV report |
| `results_generate_pdf` | Generate PDF report |
| `results_generate_all` | Generate all report formats |
| `results_tags` | List result tags |

### Resources — 17 tools

Browse and manage application resources, attacks, TLS certificates, captures, and more.

| Tool | Description |
|---|---|
| `resources_list_apps` | List applications for traffic generation |
| `resources_get_app` | Get application details |
| `resources_list_app_types` | List application types |
| `resources_list_attacks` | List attacks/strikes for security testing |
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

### Controllers — 12 tools

Manage CyPerf controllers, compute nodes, and ports.

| Tool | Description |
|---|---|
| `controllers_list` | List controllers |
| `controllers_get` | Get controller details |
| `controllers_list_nodes` | List compute nodes |
| `controllers_get_node` | Get compute node details |
| `controllers_list_ports` | List ports on a controller |
| `controllers_get_port` | Get port details |
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

### Statistics — 6 tools

Manage statistics plugins and query test result stats.

| Tool | Description |
|---|---|
| `stats_list_plugins` | List stats plugins |
| `stats_create_plugin` | Create a stats plugin |
| `stats_delete_plugin` | Delete a stats plugin |
| `stats_ingest` | Ingest external statistics |
| `stats_get_result_stats` | Get stats for a test result |
| `stats_get_result_stat` | Get a specific stat by name |

### Certificates — 3 tools

Manage controller certificates.

| Tool | Description |
|---|---|
| `certs_list` | List certificates |
| `certs_generate` | Generate a certificate |
| `certs_upload` | Upload a certificate |

### System — 10 tools

System utilities: time, disk, EULA, logging.

| Tool | Description |
|---|---|
| `system_get_time` | Get server time |
| `system_get_disk_usage` | Get disk usage overview |
| `system_list_disk_consumers` | List disk consumers |
| `system_cleanup_diagnostics` | Clean up diagnostics disk |
| `system_cleanup_logs` | Clean up logs |
| `system_cleanup_results` | Clean up test results |
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
1. sessions_list                              → find or note available sessions
2. sessions_create  session_data={...}        → create a new session
3. sessions_load_config  session_id, config_url  → load a test config
4. agents_list                                → see available agents
5. test_init  session_id                      → initialize the test
6. test_start  session_id                     → start the test run
7. sessions_get_test  session_id              → check test status
8. test_stop  session_id                      → stop when done
9. results_list                               → find the result
10. results_get_stats  result_id              → view statistics
11. results_generate_pdf  result_id           → generate PDF report
```

### Security Assessment

```
1. resources_list_attacks                     → browse available attacks/strikes
2. resources_list_attack_categories           → see attack categories
3. sessions_create  session_data={...}        → create session
4. sessions_add_applications  session_id, app_ids  → add attack applications
5. test_start  session_id                     → run the security test
6. results_get_stats  result_id              → analyze security results
```

### Infrastructure Management

```
1. controllers_list                           → list controllers
2. controllers_list_nodes  controller_id      → inspect compute nodes
3. agents_list                                → view all agents
4. agents_reserve  agent_ids=[...]            → reserve agents
5. system_get_disk_usage                      → check disk space
6. licensing_list_licenses                    → check license status
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

Async operations (test start/stop, batch deletes, exports) are automatically polled to completion with a default timeout of 300 seconds.

## Development

```bash
# Install in development mode
pip install -e .

# Run with MCP Inspector for interactive testing
mcp dev src/cyperf_mcp/cyperf_mcp_server.py
```

## License

Proprietary — Keysight Technologies.
