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

# Add 7 LLM/HTTP applications (auto-creates traffic profile if none exists)
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
licensing_manage_server(action="add",host="3.142.185.122",
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

### Scenario 10 — Real World Age Group Mix (1000 Simulated Users)

**Script:** N/A (built interactively via MCP tools)
**Config:** `appsec-416`
**Base config:** `appsec-consumer-internet-traffic-mix`
**Purpose:** Simulate realistic internet traffic from different age demographics — teens, young adults, working adults, and seniors — with 1000 concurrent users.

**Age group app mapping:**

| Age Group | Apps |
|-----------|------|
| Teens (13-17) | TikTok, Instagram, Snapchat Web Chrome, Youtube Chrome |
| Young Adults (18-30) | Netflix, X.com, Facebook Chrome, Youtube Music, Amazon E-commerce |
| Working Adults (30-50) | Office365 Outlook Chrome, Office365 OneDrive Chrome, Microsoft Teams Presenter - New User, LinkedIn, Microsoft Whiteboard |
| Seniors / General | AOL Mail (x3), Gettr IE, EpixNow Edge, Facebook Audio Edge |
| Infrastructure | SMTP (x2), POP3, DNS Flood |

```
# Start from consumer internet traffic mix base (keeps existing 11 apps)
sessions_create(config_url="appsec-consumer-internet-traffic-mix")

# Add age-group apps one at a time (batch fails if any single app errors)
sessions_add_applications(session_id, app_names=["TikTok"])
sessions_add_applications(session_id, app_names=["Instagram"])
sessions_add_applications(session_id, app_names=["Snapchat Web Chrome"])
sessions_add_applications(session_id, app_names=["Youtube Chrome"])
sessions_add_applications(session_id, app_names=["Netflix"])
sessions_add_applications(session_id, app_names=["X.com"])
sessions_add_applications(session_id, app_names=["Facebook Chrome"])
sessions_add_applications(session_id, app_names=["Youtube Music"])
sessions_add_applications(session_id, app_names=["Amazon E-commerce"])
sessions_add_applications(session_id, app_names=["Office365 Outlook Chrome"])
sessions_add_applications(session_id, app_names=["Office365 OneDrive Chrome"])
sessions_add_applications(session_id, app_names=["Microsoft Teams Attendee - Video Meeting"])
sessions_add_applications(session_id, app_names=["LinkedIn"])

# ... assign agents, set static IPs (standard config)
sessions_set_objective_and_timeline(session_id,
    objective_type="SIMULATED_USERS", objective_value=1000, duration=120)
test_start(session_id)
# Long-lived sessions — stop manually after ~140s
test_stop(session_id)
results_stats(result_id, stat_id="client-traffic-profile")
sessions_save_config(session_id, name="Real World Age Group Mix")
sessions_delete(session_id)
```

**Notes:**
- Some apps (Google Docs, Gmail Chrome, CNN, Google Search) return 404 on this controller — excluded from the mix
- Add apps individually to isolate failures (batch add is all-or-nothing)
- Base config contributes 11 pre-existing apps (AOL Mail, SMTP, POP3, DNS Flood, etc.)

**Expected:** All 24 apps generate traffic. Netflix dominates bandwidth (~3 GB). DNS Flood runs ~31M flows. Some web app session timeouts expected at 1000 users on a single agent pair.

---

### Scenario 11 — Session Introspection and Modification Workflow

**Purpose:** Exercises the session query/update tools not covered by build-from-scratch or load-and-run scenarios. Covers: `sessions_list`, `sessions_get`, `sessions_update`, `sessions_get_config`, `sessions_load_config`, `sessions_get_meta`, `sessions_get_test`.

```
# List all active sessions
sessions_list()
sessions_list(search_col="name", search_val="LLM", filter_mode="contains")

# Create a blank session and inspect it
sessions_create()
sessions_get(session_id)
sessions_get_config(session_id)
sessions_get_meta(session_id)
sessions_get_test(session_id)

# Update session properties (e.g., description)
sessions_update(session_id, properties={"description": "MCP playbook test session"})

# Touch to keep session alive (resets idle timeout)

# Load a saved config into the existing session (replaces current config)
sessions_load_config(session_id, config_url="appsec-276")

# Verify config loaded correctly
sessions_get_config(session_id)
sessions_get(session_id)

# Clean up
sessions_delete(session_id)
```

**Expected:** All introspection calls return valid JSON. `sessions_update` changes description. `sessions_load_config` replaces session config with `appsec-276`.

---

### Scenario 12 — Application and Attack Profile Management

**Purpose:** Exercises the full lifecycle of adding, listing, and removing individual applications and attacks. Covers: `sessions_get_applications`, `sessions_get_attacks`, `sessions_remove_application`, `sessions_remove_attack`, `sessions_rename_network_segments`.

```
# Create a blank session
sessions_create()

# Add several applications
sessions_add_applications(session_id, app_names=["HTTP App", "ChatGPT", "Netflix"])

# List all applications in the traffic profile
sessions_get_applications(session_id)

# Remove one application by ID (Netflix)
sessions_remove_application(session_id, app_id=<netflix_app_id>)

# Verify removal
sessions_get_applications(session_id)
# Expected: only HTTP App and ChatGPT remain

# Add attacks
sessions_add_attacks(session_id, attack_names=[
    "SQL Injection Attacks",
    "XSS Attacks",
    "DAN Jailbreak Attack on LLM - Variant 1"
])

# List all attacks in the attack profile
sessions_get_attacks(session_id)

# Remove one attack by ID (XSS)
sessions_remove_attack(session_id, attack_id=<xss_attack_id>)

# Verify removal
sessions_get_attacks(session_id)
# Expected: only SQL Injection and DAN Jailbreak remain

# Rename network segments
sessions_get_network_segments(session_id)
sessions_rename_network_segments(session_id, renames={
    <original_client_segment_name>: "TestClient",
    <original_server_segment_name>: "TestServer"
})

# Verify rename
sessions_get_network_segments(session_id)
# Expected: segments named "TestClient" and "TestServer"

# Clean up
sessions_delete(session_id)
```

**Expected:** Applications/attacks are added, listed, individually removed, and verified. Segments are renamed successfully.

---

### Scenario 13 — Test Lifecycle Control (start/abort/calibrate)

**Purpose:** Exercises test lifecycle tools beyond simple start/stop. Covers: `test_start`, `test_stop(force=True)`, `test_calibrate`.

```
# Create session from a simple config
sessions_create(config_url="appsec-appmix")
sessions_add_applications(session_id, app_names=["HTTP App"])
# ... assign agents, set static IPs (standard config)

# --- Flow A: Start → abort (immediate halt, no ramp-down) ---
test_start(session_id)
# Let it run briefly (~15s)

test_stop(session_id, force=True)
# Expected: test immediately terminates, session goes to STOPPED

sessions_delete(session_id)

# --- Flow B: Calibrate before test ---
sessions_create(config_url="appsec-appmix")
sessions_add_applications(session_id, app_names=["HTTP App"])
# ... assign agents, set static IPs (standard config)

# Calibrate adjusts agent performance parameters
test_calibrate(session_id, action="start")
# Wait for calibration to complete
test_calibrate(session_id, action="stop")

# Now run the test normally
test_start(session_id)
# Let it run briefly
test_stop(session_id)

sessions_delete(session_id)
```

**Expected:** Flow A: start→abort terminates test immediately. Flow B: calibration completes without error, subsequent test runs normally.

**Notes:**
- `test_stop(force=True)` is destructive — use only when graceful `test_stop` is insufficient
- `test_calibrate` is optional and adjusts agent-level settings before a run
- `test_init`, `test_prepare`, and `test_end` were removed — `test_start` handles init+prepare automatically, and the controller auto-ends tests on stop/abort

---

### Scenario 14 — Config Import/Export Round-Trip

**Purpose:** Exercises config import/export tools and categories. Covers: `configs_import` (with `import_all` flag), `configs_export_all`, `configs_categories`.

```
# List config categories
configs_categories()
# Expected: list of category names (e.g., "Application Security", "Performance", etc.)

# Export all configs (or a subset) as a zip archive
configs_export_all()
# Expected: returns a download path/URL for the exported zip

# Export specific configs by ID
configs_list(search_col="displayName", search_val="LLM", filter_mode="contains")
configs_export_all(config_ids=[<config_id_1>, <config_id_2>])

# Import a single config from file
configs_import(file_path="/tmp/exported-config.json")
# Expected: new config created, returns config ID

# Import all configs from a zip archive
configs_import(import_all=True,file_path="/tmp/exported-configs.zip")
# Expected: all configs from the archive are imported

# Verify imported configs appear in list
configs_list()

# Clean up imported test configs
configs_delete(config_ids=[<imported_config_id>])
```

**Expected:** Export produces downloadable archives. Import creates new configs that appear in the config list. Round-trip preserves config integrity.

---

### Scenario 15 — Results Deep Dive and Config Download

**Purpose:** Exercises results tools not covered by basic stat collection. Covers: `results_download_config`.

```
# Run a quick test first (reuse Scenario 3 — fast attack-only)
sessions_create(config_url="appsec-all-dan-ai-prompt-injection-attacks")
# ... assign agents, set static IPs (standard config)
test_start(session_id)
# Wait for auto-completion (~15s)
results_stats(result_id, stat_id="all")

# Download the config snapshot saved with the result
results_download_config(result_id)
# Expected: returns the config JSON as it was at test execution time

# Get specific stat views
results_stats(result_id, stat_id="client-attack-profile")
results_stats(result_id, stat_id="client-attack-objectives")

# List result files and get individual file
results_files(result_id)
results_files(result_id, file_id=<specific_file_id>)

# Generate reports in all formats
results_generate_report(result_id, format="pdf")
results_generate_report(result_id, format="csv")
results_generate_report(result_id, format="all")

# Tag and clean up
results_tags(result_id, tags=["playbook-validated"])
sessions_delete(session_id)
results_delete(result_ids=[result_id])
```

**Expected:** `results_download_config` returns the original test config. Reports generate in all formats. Tags are applied.

---

## Part B — Tool Smoke Tests

Quick targeted tests for individual tool categories that aren't fully
exercised by the end-to-end scenarios above.

### B1 — Resource search (list/get/search modes)

```
# --- List mode (resources_list_apps/attacks with full search/filter) ---
resources_list_apps()
resources_list_apps(take=5, skip=0)
resources_list_attacks()
resources_list_attacks(take=10, skip=0)

# --- Search mode (substring match on name/description) ---
resources_search(resource_type="apps", query="HTTP")
resources_search(resource_type="apps", query="ChatGPT")
resources_search(resource_type="attacks", query="Jailbreak")
resources_search(resource_type="attacks", query="SQL Injection")

# --- Get by ID mode ---
resources_search(resource_type="app", resource_id="192")
resources_search(resource_type="attack", resource_id="2233")

# --- List mode (browse all 9 catalog types) ---
resources_search(resource_type="app_types")
resources_search(resource_type="attack_categories")
resources_search(resource_type="captures")
resources_search(resource_type="tls_certs")
resources_search(resource_type="pcaps")
resources_search(resource_type="payloads")
resources_search(resource_type="auth_profiles")
resources_search(resource_type="http_profiles")
resources_search(resource_type="custom_fuzzing")

# --- List mode with pagination ---
resources_search(resource_type="app_types", take=3)
resources_search(resource_type="payloads", take=2, skip=5)

# --- Corner cases ---
# Invalid resource_type for list mode → should return clear error
resources_search(resource_type="invalid_type")
# Expected: error with valid types listed

# resource_id takes priority over query (query ignored)
resources_search(resource_type="app", resource_id="192", query="ignored")
# Expected: returns app 192, query is ignored

# Search with empty result
resources_search(resource_type="apps", query="xyznonexistent12345")
# Expected: {"count": 0, "matches": []}

# Get by ID with invalid ID → should return API error
resources_search(resource_type="app", resource_id="99999999")
# Expected: error (not found)
```

### B1b — Resource CRUD (captures, TLS certs)

```
# Captures: list → get → delete
resources_search(resource_type="captures")
resources_search(resource_type="capture", resource_id=<id>)
resources_delete(resource_type="capture", resource_id=<id>)
# Note: requires an existing capture from a prior test run

# TLS certs: list → get → delete
resources_search(resource_type="tls_certs")
resources_search(resource_type="tls_cert", resource_id=<id>)
resources_delete(resource_type="tls_cert", resource_id=<id>)
# Note: upload a test cert first via certs_upload or use an existing one
```

**Expected:** Get returns detailed metadata for the resource. Delete removes it from the list. Verify with a follow-up list call.

---

### B2 — Agent management

```
agents_list()
agents_list(search_col="managementIp", search_val="10.36.74", filter_mode="startsWith")
agents_get(agent_id=<id>)
agents_reserve(agent_ids=[<id>])
agents_tags(agent_ids=[<id>], tags=["mcp-test"])
agents_release(agent_ids=[<id>])
```

### B2b — Agent configuration and maintenance

```
# Update agent properties (e.g., display name)
agents_update(agent_id=<id>, properties={"displayName": "MCP-Test-Agent"})
agents_get(agent_id=<id>)
# Expected: displayName updated

# Configure DPDK (enable/disable hardware acceleration)
agents_set_dpdk(agent_ids=[<id>], enabled=true)
agents_get(agent_id=<id>)
# Expected: DPDK enabled on agent

agents_set_dpdk(agent_ids=[<id>], enabled=false)
# Revert to disabled

# Configure NTP server
agents_set_ntp(agent_ids=[<id>], ntp_server="pool.ntp.org")
agents_get(agent_id=<id>)
# Expected: NTP server set

# Export agent diagnostic files
agents_export_files(agent_ids=[<id>])
agents_export_files(agent_ids=[<id>], file_type="logs")
# Expected: returns download path for agent files

# Reboot agent (DESTRUCTIVE — agent goes offline temporarily)
# agents_reboot(agent_ids=[<id>])
# Expected: agent reboots, comes back online after ~60s
# WARNING: Only run when agent is not in use

# Delete agent registration (DESTRUCTIVE — removes agent from controller)
# agents_delete(agent_ids=[<id>])
# Expected: agent removed from agents_list
# WARNING: Agent must be re-registered after deletion
```

**Expected:** Update/DPDK/NTP changes are reflected in `agents_get`. Export returns file download info. Reboot and delete are destructive — test only with disposable agents.

**Notes:**
- `agents_reboot` takes agent offline for ~60s — do not run during other tests
- `agents_delete` permanently removes agent registration — requires re-registration
- `agents_tags` without agent_ids returns the list of all tags (smoke test variant)

---

### B3 — Config management

```
configs_list()
configs_list(search_col="displayName", search_val="LLM", filter_mode="contains")
configs_export_all()
configs_update(config_id=<id>, name="MCP Test Config Renamed")
configs_delete(config_ids=[<id>])
```

### B3b — Config import/export and categories

```
# List all config categories
configs_categories()
# Expected: array of category objects with names

# Export specific configs
configs_export_all(config_ids=["appsec-276"])
# Expected: download URL for zip archive

# Import a config from file
configs_import(file_path="/tmp/test-config.json")
# Expected: new config created

# Bulk import from archive
configs_import(import_all=True,file_path="/tmp/configs-archive.zip")
# Expected: multiple configs imported

# Clean up
configs_delete(config_ids=[<imported_ids>])
```

**Expected:** Categories returns a non-empty list. Export produces a zip. Import creates new configs visible in `configs_list`.

---

### B4 — Licensing

```
licensing_list_servers()
licensing_manage_server(action="get",server_id=<id>)
licensing_test_connectivity(server_id=<id>)
licensing_sync(server_id=<id>)
licensing_list_licenses()
licensing_get_license(license_id=<id>)
licensing_get_hostid()
licensing_get_feature_stats()
licensing_get_code_info(code_type="activation",)
licensing_get_code_info(code_type="entitlement",)
```

### B4b — License server CRUD and feature reservation

```
# Add a new license server
licensing_manage_server(action="add",host="3.142.185.122",
    username="admin", password="CyPerf&Keysight#1")
# Expected: server added, connection_status eventually "CONNECTED"

# Update server properties
licensing_manage_server(action="update",server_id=<id>, properties={"description": "MCP test server"})
licensing_manage_server(action="get",server_id=<id>)
# Expected: description updated

# Test connectivity
licensing_test_connectivity(server_id=<id>)
# Expected: connectivity check passes

# Sync licenses from server
licensing_sync(server_id=<id>)
# Expected: license list refreshed

# Delete server (only if it was added by this test)
licensing_manage_server(action="delete",server_id=<id>)
licensing_list_servers()
# Expected: server removed from list

# --- License activation/deactivation ---
# NOTE: Requires valid activation/entitlement codes
# licensing_activation(action="activate",activation_code="<valid_code>")
# Expected: license activated
# licensing_activation(action="deactivate",activation_code="<valid_code>")
# Expected: license deactivated

# --- Feature reservation ---
licensing_list_licenses()
# licensing_reservation(action="reserve",license_id=<id>, feature_name="<feature>", count=1)
# Expected: feature reserved from license pool
# licensing_reservation(action="remove",license_id=<id>)
# Expected: reservation released

# Get activation and entitlement info (read-only, always safe)
licensing_get_code_info(code_type="activation",)
licensing_get_code_info(code_type="entitlement",)
licensing_get_feature_stats()
licensing_get_hostid()
```

**Expected:** Server CRUD lifecycle works. Activation/deactivation require valid codes (commented out for safety). Feature reservation requires an active license.

**Notes:**
- `licensing_activation` requires real activation codes — do not test with dummy values
- `licensing_reservation` requires an active license with available features
- `licensing_delete_server` is safe if the server was added during this test session

---

### B5 — System and diagnostics

```
system_get_time()
system_disk_usage()
system_disk_usage(detail=True)
system_eula(action="check")
system_log_config()
notifications_list()
notifications_get_counts()
diagnostics_list_components()
```

### B5b — System write operations

```
# Accept EULA (idempotent — safe to call even if already accepted)
system_eula(action="accept")
system_eula(action="check")
# Expected: EULA status is "accepted"

# Update log configuration
system_log_config()
system_log_config(config_data={"level": "DEBUG"})
system_log_config()
# Expected: log level changed to DEBUG

# Revert log config
system_log_config(config_data={"level": "INFO"})
# Expected: log level back to INFO

# System cleanup (remove old data)
system_cleanup(target="test_results")
# Expected: old test results cleaned up, disk space reclaimed
# WARNING: Removes data — only run in test environments

# Other cleanup targets
# system_cleanup(target="configs")
# system_cleanup(target="captures")
# system_cleanup(target="diagnostics")
```

**Expected:** EULA accept is idempotent. Log config changes are reflected immediately. Cleanup frees disk space.

### B5c — Diagnostics export and cleanup

```
# List available diagnostic components
diagnostics_list_components()
# Expected: list of component names (e.g., "controller", "broker", "agent-manager")

# Export diagnostics for specific components
diagnostics_export(component_names=["controller"])
# Expected: returns download path for diagnostic bundle

# Export all diagnostics (no component filter)
diagnostics_export()
# Expected: returns download path for full diagnostic bundle

# Delete old diagnostic exports
diagnostics_delete()
# Expected: clears stored diagnostic exports
```

**Expected:** Export produces downloadable diagnostic bundles. Delete cleans up stored exports.

---

### B6 — Controller and broker management

```
controllers_list()
controllers_get(controller_id=<id>)
controllers_nodes(controller_id=<id>)
controllers_ports(controller_id=<id>)
brokers_list()
brokers_manage(action="get",broker_id=<id>)
```

### B6b — Controller port and node operations

```
# Get detailed node info
controllers_nodes(controller_id=<id>)
controllers_nodes(controller_id=<id>, node_id=<node_id>)

# Get detailed port info
controllers_ports(controller_id=<id>)
controllers_ports(controller_id=<id>, port_id=<port_id>)

# Set controller application
controllers_set_app(controller_id=<id>, app_id=<app_id>)
# Expected: controller application updated

# Set port link state (up/down)
controllers_set_link_state(controller_id=<id>, port_id=<port_id>, state="up")
controllers_set_link_state(controller_id=<id>, port_id=<port_id>, state="down")
controllers_set_link_state(controller_id=<id>, port_id=<port_id>, state="up")
# Expected: port state toggled

# Set aggregation mode on a node
controllers_set_aggregation(controller_id=<id>, node_id=<node_id>, mode="LACP")
# Expected: aggregation mode changed

# Clear all port assignments
controllers_clear_ports(controller_id=<id>)
# Expected: all port assignments removed
# WARNING: Affects running tests that use these ports

# Reboot a specific port (DESTRUCTIVE)
# controllers_reboot_port(controller_id=<id>, port_id=<port_id>)
# Expected: port reboots, comes back online
# WARNING: Disrupts traffic on that port

# Power cycle nodes (DESTRUCTIVE)
# controllers_power_cycle(controller_id=<id>, node_ids=[<node_id>])
# Expected: node power cycles, comes back online after ~120s
# WARNING: Takes node fully offline — only run in maintenance windows
```

**Expected:** Read operations return valid data. Link state changes are reflected in `controllers_ports`. Destructive operations (reboot_port, power_cycle) are commented out for safety.

**Notes:**
- `controllers_clear_ports` disrupts any active test sessions
- `controllers_reboot_port` takes a port offline temporarily
- `controllers_power_cycle` is the most destructive — full node restart
- `controllers_set_aggregation` modes: typically "NONE", "LACP", "STATIC"

### B6c — Broker CRUD

```
# Create a new broker
brokers_manage(action="create",broker_data={"name": "MCP Test Broker", "host": "10.0.0.200"})
# Expected: broker created, returns broker ID

# Get the new broker
brokers_manage(action="get",broker_id=<new_id>)
# Expected: returns broker details

# Update broker properties
brokers_manage(action="update",broker_id=<new_id>, properties={"name": "MCP Test Broker Updated"})
brokers_manage(action="get",broker_id=<new_id>)
# Expected: name updated

# Delete the test broker
brokers_manage(action="delete",broker_id=<new_id>)
brokers_list()
# Expected: test broker removed from list
```

**Expected:** Full CRUD lifecycle for brokers works. Created broker appears in list, updates are reflected, delete removes it.

---

### B7 — Results and reports

```
results_list()
results_list(take=5, skip=0, sort="-startTime")
results_get(result_id=<id>)
results_stats(result_id=<id>)
results_stats(result_id=<id>, stat_id="client-traffic-profile")
results_files(result_id=<id>)
results_files(result_id=<id>, file_id=<specific_file_id>)
results_download_config(result_id=<id>)
results_generate_report(result_id=<id>, format="pdf")
results_generate_report(result_id=<id>, format="csv")
results_generate_report(result_id=<id>, format="all")
results_tags(result_id=<id>, tags=["mcp-validated"])
results_delete(result_ids=[<id>])
```

---

### B8 — Certificates

```
certs_list()
certs_generate(common_name="mcp-test.example.com")
certs_upload(file_path="/path/to/cert.pem")
```

---

### B9 — Migration

```
migration_export()
migration_import(file_path="/path/to/backup.zip")
```

---

### B10 — Notifications lifecycle

```
# List and count notifications
notifications_list()
notifications_list(take=5, skip=0)
notifications_get_counts()

# Get a specific notification by ID
notifications_get(notification_id=<id>)
# Expected: returns notification details (message, severity, timestamp)

# Dismiss all notifications (marks as read, does not delete)
notifications_manage(action="dismiss")
notifications_get_counts()
# Expected: unread count drops to 0

# Delete a specific notification
notifications_delete(notification_id=<id>)
notifications_list()
# Expected: deleted notification no longer in list

# Clean up all notifications
notifications_manage(action="cleanup")
notifications_list()
# Expected: notification list is empty (or only system-generated ones remain)
```

**Expected:** Full notification lifecycle works. Dismiss marks as read. Delete removes individual notifications. Cleanup clears all.

---

### B11 — Statistics plugins

```
# List existing stats plugins
stats_plugins(action="list")
# Expected: list of plugin objects (may be empty)

# Create a new stats plugin
stats_plugins(action="create",plugin_data={
    "name": "MCP Test Plugin",
    "type": "webhook",
    "config": {"url": "https://httpbin.org/post"}
})
# Expected: plugin created, returns plugin ID

# Verify plugin appears in list
stats_plugins(action="list")
# Expected: MCP Test Plugin in the list

# Ingest stats data into the plugin (requires an active test result)
stats_ingest(operation_data={
    "plugin_id": "<plugin_id>",
    "result_id": "<result_id>"
})
# Expected: stats data sent to the plugin endpoint

# Delete the test plugin
stats_plugins(action="delete",plugin_id=<id>)
stats_plugins(action="list")
# Expected: plugin removed from list
```

**Expected:** Plugin CRUD lifecycle works. Ingest sends data to the configured endpoint. Cleanup removes the test plugin.

**Notes:**
- `stats_ingest` requires both a valid plugin and a completed test result
- Plugin types and config schemas depend on the controller version

---

## Part C — Destructive / Conditional Tests

These tests are separated because they modify shared state, require specific
preconditions, or can disrupt other users. Run only in isolated test environments.

### C1 — Agent reboot and delete

**Precondition:** Disposable test agent not in use by any session.

```
# Reserve a disposable agent
agents_reserve(agent_ids=[<disposable_id>])

# Reboot the agent
agents_reboot(agent_ids=[<disposable_id>])
# Wait ~60s for agent to come back online
agents_get(agent_id=<disposable_id>)
# Expected: agent status returns to "READY" after reboot

# Release before delete
agents_release(agent_ids=[<disposable_id>])

# Delete agent registration
agents_delete(agent_ids=[<disposable_id>])
agents_list()
# Expected: agent no longer in list
# NOTE: Agent must be re-registered with the controller to use again
```

### C2 — Controller power cycle and port reboot

**Precondition:** No active tests running on the controller.

```
controllers_list()
controllers_nodes(controller_id=<id>)
controllers_ports(controller_id=<id>)

# Reboot a specific port
controllers_reboot_port(controller_id=<id>, port_id=<port_id>)
# Wait ~30s for port to come back
controllers_ports(controller_id=<id>, port_id=<port_id>)
# Expected: port status returns to normal

# Power cycle a node (most destructive)
controllers_power_cycle(controller_id=<id>, node_ids=[<node_id>])
# Wait ~120s for node to come back
controllers_nodes(controller_id=<id>, node_id=<node_id>)
# Expected: node status returns to normal
```

### C3 — License activation/deactivation

**Precondition:** Valid activation code available.

```
licensing_get_hostid()
licensing_get_code_info(code_type="activation",activation_code="<valid_code>")

# Activate
licensing_activation(action="activate",activation_code="<valid_code>")
licensing_list_licenses()
# Expected: new license appears

# Reserve a feature from the license
licensing_reservation(action="reserve",license_id=<id>, feature_name="<feature>", count=1)
licensing_get_feature_stats()
# Expected: feature reservation shows count=1

# Remove reservation
licensing_reservation(action="remove",license_id=<id>)
licensing_get_feature_stats()
# Expected: reservation released

# Deactivate
licensing_activation(action="deactivate",activation_code="<valid_code>")
licensing_list_licenses()
# Expected: license removed
```

### C4 — System cleanup (all targets)

**Precondition:** No important data on the controller.

```
system_disk_usage()
system_disk_usage(detail=True)

# Clean up each target
system_cleanup(target="test_results")
system_cleanup(target="configs")
system_cleanup(target="captures")
system_cleanup(target="diagnostics")

system_disk_usage()
# Expected: disk usage decreased after cleanup
```

---

## Tool coverage summary

| Category | Tools | Covered by |
|----------|-------|------------|
| Sessions (28) | sessions_list | S11 |
| | sessions_create | S1-10, S11, S12, S13 |
| | sessions_get | S11 |
| | sessions_delete | S1-13, S15 |
| | sessions_update | S11 |
| | sessions_get_config | S11 |
| | sessions_save_config | S1, S10 |
| | sessions_load_config | S11 |
| | sessions_get_meta | S11 |
| | sessions_get_test | S11 |
| | sessions_add_applications | S1, S8, S10, S12 |
| | sessions_add_attacks | S1, S8, S12 |
| | sessions_get_applications | S12 |
| | sessions_get_attacks | S12 |
| | sessions_get_app_actions | S1 |
| | sessions_remove_app_action | S1 |
| | sessions_set_app_action_param | S1 |
| | sessions_remove_application | S12 |
| | sessions_remove_attack | S12 |
| | sessions_assign_agents | S1-10, S13 |
| | sessions_rename_network_segments | S12 |
| | sessions_get_network_segments | S1-10, S12 |
| | sessions_set_network_ip_range | S1-10, S13 |
| | sessions_disable_automatic_network | S1-10, S13 |
| | sessions_set_objective_and_timeline | S1, S4-7, S10 |
| Resources (4) | resources_list_apps | B1 |
| | resources_list_attacks | B1 |
| | resources_search | B1, B1b (list/get/search modes) |
| | resources_delete | B1b |
| Licensing (17) | licensing_list_licenses | B4, C3 |
| | licensing_get_license | B4 |
| | licensing_activation (activate/deactivate) | C3 |
| | licensing_sync | B4, B4b |
| | licensing_get_hostid | B4, C3 |
| | licensing_reservation (reserve/remove) | C3 |
| | licensing_test_connectivity | B4, B4b |
| | licensing_get_code_info (activation/entitlement) | B4, B4b, C3 |
| | licensing_get_feature_stats | B4, B4b, C3 |
| | licensing_list_servers | B4, B4b |
| | licensing_manage_server (add/get/update/delete) | S1, B4, B4b |
| Agents (11) | agents_list | B2 |
| | agents_get | B2, B2b |
| | agents_delete | B2b, C1 |
| | agents_update | B2b |
| | agents_reserve | B2, C1 |
| | agents_release | B2, C1 |
| | agents_reboot | C1 |
| | agents_set_dpdk | B2b |
| | agents_set_ntp | B2b |
| | agents_tags | B2, B2b |
| | agents_export_files | B2b |
| Controllers (10) | controllers_list | B6, C2 |
| | controllers_get | B6 |
| | controllers_nodes | B6, B6b, C2 |
| | controllers_ports | B6, B6b, C2 |
| | controllers_set_app | B6b |
| | controllers_clear_ports | B6b |
| | controllers_power_cycle | C2 |
| | controllers_reboot_port | C2 |
| | controllers_set_link_state | B6b |
| | controllers_set_aggregation | B6b |
| Configs (6) | configs_list | B3, B3b |
| | configs_delete | B3, B3b, S14 |
| | configs_update | B3 |
| | configs_import | S14, B3b (import_all=True for bulk) |
| | configs_export_all | B3, B3b, S14 |
| | configs_categories | S14, B3b |
| System (5) | system_get_time | B5 |
| | system_disk_usage | B5, C4 (detail=True for consumers) |
| | system_cleanup | B5b, C4 |
| | system_eula | B5, B5b (action=check/accept) |
| | system_log_config | B5, B5b (omit config_data to get) |
| Results (8) | results_list | B7 |
| | results_get | B7 |
| | results_delete | B7, S15 |
| | results_stats | S1-10, S15, B7 |
| | results_files | S15, B7 |
| | results_download_config | S15, B7 |
| | results_generate_report | S15, B7 |
| | results_tags | S15, B7 |
| Test ops (3) | test_start | S1-10, S13, S15 |
| | test_stop | S1-10, S13 (force=True for abort) |
| | test_calibrate | S13 |
| Notifications (5) | notifications_list | B5, B10 |
| | notifications_get | B10 |
| | notifications_delete | B10 |
| | notifications_manage (dismiss) | B10 |
| | notifications_manage (cleanup) | B10 |
| | notifications_get_counts | B5, B10 |
| Brokers (5) | brokers_list | B6 |
| | brokers_manage (create/get/update/delete) | B6, B6c |
| Statistics (2) | stats_plugins (list/create/delete) | B11 |
| | stats_ingest | B11 |
| Diagnostics (3) | diagnostics_list_components | B5, B5c |
| | diagnostics_export | B5c |
| | diagnostics_delete | B5c |
| Certificates (3) | certs_list | B8 |
| | certs_generate | B8 |
| | certs_upload | B8 |
| Migration (2) | migration_export | B9 |
| | migration_import | B9 |

**Total: 139/139 tools covered across 15 end-to-end scenarios + 17 smoke tests + 4 destructive tests**

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
| `appsec-416` | Real World Age Group Mix (24 apps, 1000 users) |
