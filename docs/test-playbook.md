# CyPerf MCP Tools — Test Playbook

Use cases verified against the CyPerf MCP server. Each scenario lists the
exact MCP tool calls in order so they can be replayed to regression-test the tools.

Reference scripts in `comparative-studies/scripts/` implement these same scenarios using the SDK directly.

---

## Environment

| Item | Value |
|------|-------|
| Controller | `https://10.36.75.34` |
| Config profile | `partha_local_setup` |
| License server | `3.142.185.122` (user: `admin`, pass: `CyPerf&Keysight#1`) |
| Client agent | `1d3f9066-a9d9-49e9-a698-1efa7be52d49` (10.36.74.142) |
| Server agent | `2fc6d0bb-ea56-456b-9d3a-08b13f561558` (10.36.74.181) |

### Standard network config (used by most scenarios)

| Segment | IP start | Count | Prefix | Gateway |
|---------|----------|-------|--------|---------|
| Client (first segment) | 10.0.0.10 | 100 | /16 | 10.0.0.1 |
| Server (second segment) | 10.0.0.110 | 1 | /16 | 10.0.0.1 |

---

## Part A — End-to-End Test Scenarios

These mirror the Python scripts in `scripts/`. Each creates a session from
a saved config, configures network/agents, runs the test, collects stats, and cleans up.

### Common steps (all scenarios)

Every scenario follows this pattern unless noted otherwise:

```
# 1. Create session from saved config
sessions_create(config_url="<config_url>")

# 2. Get network segments and assign agents
sessions_get_network_segments(session_id)
sessions_assign_agents(session_id,
    client_agent_ids=["1d3f9066-a9d9-49e9-a698-1efa7be52d49"],
    server_agent_ids=["2fc6d0bb-ea56-456b-9d3a-08b13f561558"])

# 3. Disable auto networking and set static IPs
sessions_disable_automatic_network(session_id)
sessions_set_network_ip_range(session_id, segment_name=<first_segment>,
    ip_start="10.0.0.10", count=100, prefix=16, gateway="10.0.0.1")
sessions_set_network_ip_range(session_id, segment_name=<second_segment>,
    ip_start="10.0.0.110", count=1, prefix=16, gateway="10.0.0.1")

# 4. Set objective (scenario-specific, see below)
sessions_set_objective_and_timeline(session_id, ...)

# 5. Start test
test_start(session_id)

# 6. Monitor / wait / stop
results_stats(result_id, stat_id="all")
test_stop(session_id)

# 7. Clean up
sessions_delete(session_id)
```

---

### Scenario 1 — LLM AppMix Test (build from scratch)

**Script:** N/A (built interactively via MCP tools in a prior session)
**Purpose:** Exercises the full session-building workflow — creating profiles, adding apps/attacks, customizing actions, and configuring networks from scratch.

```
# Create a blank session
sessions_create()

# Remove default profiles
sessions_delete_traffic_profile(session_id)
sessions_delete_attack_profile(session_id)

# Add 7 LLM/HTTP applications
sessions_add_applications(session_id, app_names=[
    "AI LLM over Generic HTTP", "ChatGPT", "ChatGPT4",
    "Claude AI", "Gemini API", "Grok API", "HTTP App"
])

# Customize HTTP App: remove POST, set response body = 1MB
sessions_get_app_actions(session_id, app_name="HTTP App")
sessions_remove_app_action(session_id, action_id=<POST_action_id>)
sessions_set_app_action_param(session_id, action_id=<GET_action_id>,
    param_name="Response Body Size", param_value="1000000")

# Add 6 LLM attacks (3 DAN bundles + 3 Forbidden Questions)
sessions_add_attacks(session_id, attack_names=[
    "All DAN OpenAI ChatGPT AI LLM Prompt Injection",
    "All DAN Gemini AI LLM Prompt Injection",
    "All DAN Grok AI LLM Prompt Injection",
    "OpenAI ChatGPT Forbidden Questions AI LLM Prompt Injection",
    "Gemini Forbidden Questions AI LLM Prompt Injection",
    "Grok Forbidden Questions AI LLM Prompt Injection"
])

# Assign agents, configure network (standard config)
# ... (see common steps above)

# Set objective
sessions_set_objective_and_timeline(session_id,
    objective_type="Throughput", objective_value=100,
    duration=120, ramp_up=30, ramp_down=30)

# Add license server
licensing_add_server(host="3.142.185.122",
    username="admin", password="CyPerf&Keysight#1")

# Save, run, monitor, stop, clean up
sessions_save_config(session_id, name="LLM AppMix Test")
test_start(session_id)
results_stats(result_id, stat_id="all")
test_stop(session_id)
sessions_delete(session_id)
```

**Expected:** All 7 apps and 6 attacks run with zero errors. Saved as config `appsec-276`.

---

### Scenario 2 — LLM API Stress Test (from saved config)

**Script:** `comparative-studies/scripts/test_llm_api_stress.py`
**Config:** `appsec-276`
**Purpose:** Reload the saved LLM AppMix config and re-run it. Validates config loading and the full test lifecycle with a pre-built config.

```
sessions_create(config_url="appsec-276")
# Network segments are already named "Client Network" / "Server Network"
# ... assign agents, set static IPs (standard config)
# Built-in timeline — do NOT override objective
test_start(session_id)
# Stop after ~130s (built-in timeline ignores duration setting)
test_stop(session_id)
results_stats(result_id, stat_id="all")
sessions_delete(session_id)
```

**Expected:** Same results as Scenario 1. Test uses its own built-in timeline.

---

### Scenario 3 — AI Prompt Injection Attacks (attack-only)

**Script:** `comparative-studies/scripts/test_ai_prompt_injection.py`
**Config:** `appsec-all-dan-ai-prompt-injection-attacks`
**Purpose:** Attack-only config with no traffic profile. Validates attack execution without apps.

```
sessions_create(config_url="appsec-all-dan-ai-prompt-injection-attacks")
# ... assign agents, set static IPs (standard config)
# Attack-only: do NOT set objective or configure traffic profile
test_start(session_id)
# Completes quickly (~15s), wait for auto-stop
results_stats(result_id, stat_id="all")
sessions_delete(session_id)
```

**Expected:** All DAN prompt injection attacks execute. Check `client-attack-profile` stats for strikes attempted/blocked.

---

### Scenario 4 — Enterprise Datacenter Traffic Mix

**Script:** `comparative-studies/scripts/test_enterprise_mix.py`
**Config:** `appsec-enterprise-datacenter-traffic-mix`
**Purpose:** Broad application mix simulating enterprise datacenter traffic. Long-lived sessions.

```
sessions_create(config_url="appsec-enterprise-datacenter-traffic-mix")
# ... assign agents, set static IPs (standard config)
sessions_set_objective_and_timeline(session_id,
    objective_type="SIMULATED_USERS", objective_value=100, duration=60)
test_start(session_id)
# Long-lived sessions may not complete — stop after ~90s
test_stop(session_id)
results_stats(result_id, stat_id="all")
sessions_delete(session_id)
```

**Expected:** Multiple enterprise apps run concurrently. No failed connections/apps in summary stats.

---

### Scenario 5 — DDoS DNS Flood

**Script:** `comparative-studies/scripts/test_ddos_dns_flood.py`
**Config:** `appsec-ddos---dns-flood`
**Purpose:** High-volume DNS flood test. Validates UDP-based attack traffic.

```
sessions_create(config_url="appsec-ddos---dns-flood")
# ... assign agents, set static IPs (standard config)
sessions_set_objective_and_timeline(session_id,
    objective_type="SIMULATED_USERS", objective_value=100, duration=60)
test_start(session_id)
# Wait up to 120s for completion
results_stats(result_id, stat_id="all")
sessions_delete(session_id)
```

**Expected:** DNS flood traffic generated successfully. Check UDP stats for drops.

---

### Scenario 6 — Office 365 Outlook (Simulated Users)

**Script:** `comparative-studies/scripts/test_office365_outlook.py`
**Config:** `appsec-office365-outlook-simulated-users`
**Purpose:** Connection-heavy Office 365 Outlook simulation.

```
sessions_create(config_url="appsec-office365-outlook-simulated-users")
# ... assign agents, set static IPs (standard config)
sessions_set_objective_and_timeline(session_id,
    objective_type="SIMULATED_USERS", objective_value=100, duration=60)
test_start(session_id)
# Wait up to 120s
results_stats(result_id, stat_id="all")
sessions_delete(session_id)
```

**Expected:** Outlook traffic simulated with 100 users. No failed connections.

---

### Scenario 7 — Office 365 OneDrive (Simulated Users)

**Script:** `comparative-studies/scripts/test_office365_onedrive.py`
**Config:** `appsec-office365-onedrive-simulated-users`
**Purpose:** Upload-heavy Office 365 OneDrive simulation.

```
sessions_create(config_url="appsec-office365-onedrive-simulated-users")
# ... assign agents, set static IPs (standard config)
sessions_set_objective_and_timeline(session_id,
    objective_type="SIMULATED_USERS", objective_value=100, duration=60)
test_start(session_id)
# Wait up to 120s
results_stats(result_id, stat_id="all")
sessions_delete(session_id)
```

**Expected:** OneDrive upload traffic simulated. No failed connections.

---

### Scenario 8 — WAF Validation (AppMix + Attacks)

**Script:** `comparative-studies/scripts/test_waf_validation.py`
**Config:** `appsec-appmix-and-attack`
**Purpose:** Mixed traffic and attack test for WAF validation. Adds extra apps and attacks on top of the saved config.

```
sessions_create(config_url="appsec-appmix-and-attack")
# ... assign agents, set static IPs (standard config)
sessions_set_objective_and_timeline(session_id,
    objective_type="SIMULATED_USERS", objective_value=100, duration=60)

# Add extra applications and attacks on top of the config
sessions_add_applications(session_id, app_names=["HTTP App"])
sessions_add_attacks(session_id, attack_names=[
    "SQL Injection Attacks",
    "XSS Attacks"
])

test_start(session_id)
# Wait up to 120s
results_stats(result_id, stat_id="all")
sessions_delete(session_id)
```

**Expected:** HTTP App traffic runs alongside SQL Injection and XSS attacks. Check `client-attack-profile` for strikes blocked vs attempted.

---

### Scenario 9 — TLS 1.3 Throughput (AES-256-GCM-SHA384)

**Script:** `comparative-studies/scripts/test_tls_throughput.py`
**Config:** `appsec-https-tls1.3-throughput-aws-within-vpc-c5n.9xlarge-(aes-256-gcm-sha384)`
**Purpose:** Sustained throughput test targeting 10 Gbps over TLS 1.3. Includes time-series throughput analysis.

```
sessions_create(config_url="appsec-https-tls1.3-throughput-aws-within-vpc-c5n.9xlarge-(aes-256-gcm-sha384)")
# ... assign agents, set static IPs (standard config)
sessions_set_objective_and_timeline(session_id,
    objective_type="THROUGHPUT", objective_value=10, duration=300)
test_start(session_id)
# Wait up to 360s for completion
results_stats(result_id, stat_id="all")
# Also check throughput time-series for sustained performance
sessions_delete(session_id)
```

**Expected:** Sustained ~10 Gbps throughput. Steady-state average should be ≥90% of target. Ramp-up in first 20%, ramp-down in last 10%.

---

## Part B — Tool Smoke Tests

Quick targeted tests for individual tool categories that aren't fully
exercised by the end-to-end scenarios above.

### B1 — Resource browsing and search

```
resources_list_apps()
resources_search_apps(query="HTTP")
resources_search_apps(query="ChatGPT")
resources_get_app(app_name="HTTP App")
resources_list_attacks()
resources_search_attacks(query="Jailbreak")
resources_search_attacks(query="SQL Injection")
resources_get_attack(attack_name="DAN Jailbreak Attack on LLM - Variant 1")
resources_list_app_types()
resources_list_attack_categories()
resources_list_captures()
resources_list_tls_certs()
resources_list_pcaps()
resources_list_payloads()
resources_list_auth_profiles()
resources_list_http_profiles()
resources_list_custom_fuzzing()
```

### B2 — Agent management

```
agents_list()
agents_get(agent_id=<id>)
agents_reserve(agent_ids=[<id>])
agents_tags(agent_ids=[<id>], tags=["mcp-test"])
agents_release(agent_ids=[<id>])
```

### B3 — Config management

```
configs_list()
configs_list(search_col="displayName", search_val="LLM", filter_mode="contains")
configs_get(config_id="appsec-276")
configs_export_all()
configs_create(name="MCP Test Config")
configs_update(config_id=<id>, name="MCP Test Config Renamed")
configs_delete(config_ids=[<id>])
```

### B4 — Licensing

```
licensing_list_servers()
licensing_get_server(server_id=<id>)
licensing_test_connectivity(server_id=<id>)
licensing_sync(server_id=<id>)
licensing_list_licenses()
licensing_get_license(license_id=<id>)
licensing_get_hostid()
licensing_get_feature_stats()
licensing_get_activation_info()
licensing_get_entitlement_info()
```

### B5 — System and diagnostics

```
system_get_time()
system_get_disk_usage()
system_list_disk_consumers()
system_check_eula()
system_get_log_config()
notifications_list()
notifications_get_counts()
diagnostics_list_components()
```

### B6 — Controller and broker management

```
controllers_list()
controllers_get(controller_id=<id>)
controllers_nodes(controller_id=<id>)
controllers_ports(controller_id=<id>)
brokers_list()
brokers_get(broker_id=<id>)
```

### B7 — Results and reports

```
results_list()
results_get(result_id=<id>)
results_stats(result_id=<id>)
results_files(result_id=<id>)
results_generate_report(result_id=<id>, format="pdf")
results_generate_report(result_id=<id>, format="csv")
results_tags(result_id=<id>, tags=["mcp-validated"])
results_delete(result_ids=[<id>])
```

### B8 — Certificates

```
certs_list()
certs_generate(common_name="mcp-test.example.com")
certs_upload(file_path="/path/to/cert.pem")
```

### B9 — Migration

```
migration_export()
migration_import(file_path="/path/to/backup.zip")
```

---

## Tool coverage summary

| Category | Tools | Covered by |
|----------|-------|------------|
| Sessions | 28 | Scenarios 1-9 |
| Resources | 19 | Scenarios 1, 8, B1 |
| Licensing | 17 | Scenario 1, B4 |
| Agents | 11 | All scenarios (agent assign), B2 |
| Controllers | 10 | B6 |
| Configs | 9 | Scenario 2, B3 |
| System | 8 | B5 |
| Results | 8 | All scenarios (stats), B7 |
| Test ops | 7 | All scenarios |
| Notifications | 6 | B5 |
| Brokers | 5 | B6 |
| Statistics | 4 | All scenarios |
| Diagnostics | 3 | B5 |
| Certificates | 3 | B8 |
| Migration | 2 | B9 |

**Total: 140 tools across 9 end-to-end scenarios + 9 smoke tests**

---

## Key stat IDs for analysis

These are the most useful stat IDs to check after a test run:

| Stat ID | Description |
|---------|-------------|
| `client-traffic-profile` | Per-app traffic summary |
| `client-attack-profile` | Per-attack strikes attempted/blocked/successful |
| `client-traffic-profile-tcp` | TCP connection stats (failed, timed out) |
| `client-http-statistics` | HTTP request/response stats |
| `server-http-statistics` | Server-side HTTP stats |
| `client-latency` | Request latency percentiles |
| `client-action-statistics` | Per-action success/failure |
| `client-attack-objectives` | Attack objective results |
| `client-throughput` | Throughput time-series (for Scenario 9) |

---

## Saved config IDs

| Config URL | Description |
|------------|-------------|
| `appsec-276` | LLM AppMix Test (7 apps + 6 attacks) |
| `appsec-all-dan-ai-prompt-injection-attacks` | DAN prompt injection attacks only |
| `appsec-enterprise-datacenter-traffic-mix` | Enterprise datacenter traffic |
| `appsec-ddos---dns-flood` | DDoS DNS flood |
| `appsec-office365-outlook-simulated-users` | Office 365 Outlook |
| `appsec-office365-onedrive-simulated-users` | Office 365 OneDrive |
| `appsec-appmix-and-attack` | AppMix + attack base (for WAF validation) |
| `appsec-https-tls1.3-throughput-aws-within-vpc-c5n.9xlarge-(aes-256-gcm-sha384)` | TLS 1.3 throughput |
