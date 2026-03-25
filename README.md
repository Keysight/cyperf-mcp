# CyPerf MCP Server

An [MCP](https://modelcontextprotocol.io/) (Model Context Protocol) server that exposes [Keysight CyPerf](https://www.keysight.com/us/en/products/network-test/protocol-load-test/cyperf.html) network performance and security testing functionality as **108 tools** across 15 categories.

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
    ├── sessions.py        # Session & config management (28 tools)
    ├── resources.py       # Apps, attacks, TLS, captures (6 tools)
    ├── licensing.py       # License management (12 tools)
    ├── agents.py          # Agent management (11 tools)
    ├── controllers.py     # Controller and port management (10 tools)
    ├── results.py         # Results and reporting (8 tools)
    ├── configs.py         # Configuration management (7 tools)
    ├── system.py          # System utilities (5 tools)
    ├── notifications.py   # Notification management (5 tools)
    ├── test_ops.py        # Test execution (4 tools)
    ├── diagnostics.py     # Diagnostics export/cleanup (3 tools)
    ├── certificates.py    # Certificate management (3 tools)
    ├── brokers.py         # Broker management (2 tools)
    ├── statistics.py      # Statistics plugins (2 tools)
    └── migration.py       # Data migration (2 tools)
```

The server wraps the [`cyperf`](https://pypi.org/project/cyperf/) Python SDK's API classes directly. Each tool module follows a class-based pattern where a `*Tools` class holds the API logic, and a `register()` function wires `@mcp.tool()` decorated functions to those methods. Session config manipulation uses the SDK's DynamicModel pattern for in-place updates.

## Tool Catalog (108 tools)

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
| `sessions_save_config` | Save session as a reusable config (this is how to create new configs) |
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

### Configurations — 7 tools

Manage saved test configurations (templates).

| Tool | Description |
|---|---|
| `configs_list` | List configurations with optional search/filter (includes PQC/Kyber/TLS configs) |
| `configs_get` | Get configuration by ID |
| `configs_delete` | Delete one or more configurations |
| `configs_update` | Update configuration metadata |
| `configs_import` | Import configuration(s) from file (`import_all=True` for bulk) |
| `configs_export_all` | Export configurations |
| `configs_categories` | List configuration categories |

### Test Operations — 4 tools

Control test execution lifecycle.

| Tool | Description |
|---|---|
| `test_start` | Start a test run (handles init+prepare automatically, polls until running) |
| `test_stop` | Stop a running test gracefully |
| `test_abort` | Abort a test run immediately |
| `test_calibrate` | Start or stop test calibration |

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

### Resources — 6 tools

Browse and search application resources, attacks, TLS certificates, captures, and more.

| Tool | Description |
|---|---|
| `resources_list_apps` | List applications with optional search/filter |
| `resources_list_attacks` | List attacks/strikes with optional search/filter |
| `resources_browse` | Browse resource catalogs by type: `app_types`, `attack_categories`, `auth_profiles`, `captures`, `tls_certs`, `custom_fuzzing`, `payloads`, `pcaps`, `http_profiles` |
| `resources_get` | Get resource details by type (`app`, `attack`, `capture`, `tls_cert`) and ID |
| `resources_delete` | Delete resource by type (`capture`, `tls_cert`, `tls_key`) and ID |
| `resources_search` | Search resources by type (`apps`, `attacks`) with substring match on name/description |

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

### Brokers — 2 tools

Manage network brokers.

| Tool | Description |
|---|---|
| `brokers_list` | List brokers |
| `brokers_manage` | Create, get, update, or delete a broker (`action`: create/get/update/delete) |

### Licensing — 12 tools

Manage licenses and license servers.

| Tool | Description |
|---|---|
| `licensing_list_licenses` | List all installed licenses |
| `licensing_get_license` | Get license details |
| `licensing_activation` | Activate or deactivate a license (`action`: activate/deactivate) |
| `licensing_sync` | Synchronize licenses |
| `licensing_get_hostid` | Get host ID |
| `licensing_reserve_feature` | Reserve a license feature |
| `licensing_remove_reservation` | Remove a reservation |
| `licensing_test_connectivity` | Test backend connectivity |
| `licensing_get_code_info` | Get activation or entitlement code info (`code_type`: activation/entitlement) |
| `licensing_get_feature_stats` | Get feature statistics |
| `licensing_list_servers` | List license servers |
| `licensing_manage_server` | Add, get, update, or delete a license server (`action`: add/get/update/delete) |

### Diagnostics — 3 tools

Export and manage diagnostic data.

| Tool | Description |
|---|---|
| `diagnostics_list_components` | List diagnostic components |
| `diagnostics_export` | Export diagnostics |
| `diagnostics_delete` | Delete diagnostics data |

### Notifications — 5 tools

Manage system notifications.

| Tool | Description |
|---|---|
| `notifications_list` | List notifications |
| `notifications_get` | Get notification details |
| `notifications_delete` | Delete a notification |
| `notifications_manage` | Dismiss or clean up notifications (`action`: dismiss/cleanup) |
| `notifications_get_counts` | Get notification counts |

### Statistics — 2 tools

Manage statistics plugins for external ingestion.

| Tool | Description |
|---|---|
| `stats_plugins` | List, create, or delete stats plugins (`action`: list/create/delete) |
| `stats_ingest` | Ingest external statistics |

### Certificates — 3 tools

Manage controller certificates.

| Tool | Description |
|---|---|
| `certs_list` | List certificates |
| `certs_generate` | Generate a certificate |
| `certs_upload` | Upload a certificate |

### System — 5 tools

System utilities: time, disk, EULA, logging.

| Tool | Description |
|---|---|
| `system_get_time` | Get server time |
| `system_disk_usage` | Get disk usage overview or detailed consumers (`detail=True`) |
| `system_cleanup` | Clean up disk space (diagnostics, logs, or results) |
| `system_eula` | Check or accept EULA (`action`: check/accept) |
| `system_log_config` | Get or set logging config (omit `config_data` to get, provide to set) |

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
