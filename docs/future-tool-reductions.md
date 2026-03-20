# Future Tool Reductions

Current tool count: **118** (down from 139 via Phase 1 consolidation + 3 removed)

## Completed Consolidations

| Phase | What | Tools Saved | Status |
|-------|------|-------------|--------|
| 1A | Resource browse (9→1) → `resources_browse` | 8 | Done |
| 1B | Resource get-by-ID (4→1) → `resources_get` | 3 | Done |
| 1C | Resource delete (2→1) → `resources_delete` | 1 | Done |
| 1D | Resource search (2→1) → `resources_search` | 1 | Done |
| 1E | Notification dismiss/cleanup → `notifications_manage` | 1 | Done |
| 1F | EULA check/accept → `system_eula` | 1 | Done |
| 1G | Log config get/set → `system_log_config` | 1 | Done |
| 1H | Disk usage overview/consumers → `system_disk_usage` | 1 | Done |
| 1I | Config import/import_all → `configs_import(import_all=)` | 1 | Done |
| — | Removed `test_init`, `test_prepare`, `test_end` (unnecessary for MCP) | 3 | Done |
| **Total saved** | | **21** | |

---

## Pending Reductions (Phase 2: Medium-Low Risk) — ~10 tools saved

### 2A. Broker CRUD (5→2) — 3 saved

Keep `brokers_list`, merge rest into `brokers_manage(action, broker_id, broker_data)`.

| Action | Required params |
|--------|----------------|
| `create` | `broker_data` |
| `get` | `broker_id` |
| `update` | `broker_id`, `broker_data` |
| `delete` | `broker_id` |

**Risk:** Low — classic CRUD dispatch, identical to `resources_get`/`resources_delete` pattern.

### 2B. Licensing server CRUD (5→2) — 3 saved

Keep `licensing_list_servers`, merge rest into `licensing_manage_server(action, server_id, server_data)`.

Same pattern as 2A.

### 2C. License activate/deactivate (2→1) — 1 saved

Merge into `licensing_activation(action, activation_code)` where action is `activate` or `deactivate`.

### 2D. License code info (2→1) — 1 saved

Merge `licensing_get_activation_info` + `licensing_get_entitlement_info` into `licensing_get_code_info(code_type, code)` where code_type is `activation` or `entitlement`.

### 2E. Stats plugins (3→1) — 2 saved

Merge `stats_list_plugins`, `stats_create_plugin`, `stats_delete_plugin` into `stats_plugins(action, plugin_id, plugin_data, take, skip)`.

**Phase 2 total: 118 → ~108**

---

## Pending Reductions (Phase 3: Medium Risk) — ~7 tools saved

### 3A. Traffic profile CRUD (4→1) — 3 saved

Merge `sessions_add_applications`, `sessions_get_applications`, `sessions_remove_application`, `sessions_delete_traffic_profile` into `sessions_traffic_profile(session_id, action, ...)`.

**Risk:** Complex conditional params — `app_names` only for `add`, `app_id` only for `remove`. These tools are on the critical test setup path.

### 3B. Attack profile CRUD (4→1) — 3 saved

Mirror of 3A for attacks.

### 3D. Migration export/import (2→1) — 1 saved

Merge into `migration(action, export_data)`.

**Phase 3 total: ~108 → ~101**

---

## Not Recommended for Consolidation

| Tools | Reason |
|-------|--------|
| `test_start/stop/abort/calibrate` | Safety-critical — must stay distinct |
| `sessions_list/create/get/delete/update` | Core CRUD, heavily used, distinct signatures |
| `sessions_get_app_actions/set_app_action_param/remove_app_action` | Deeply nested DynamicModel navigation, too complex to merge |
| `sessions_get/rename/set_network_segments + disable_automatic_network` | Critical-path for test setup |
| `agents_*` (11 tools) | Each has unique params |
| `controllers_*` (10 tools) | Hardware-only, already consolidated |
| `results_*` (8 tools) | Already consolidated, each distinct |

---

## Summary

| Phase | Savings | Target |
|-------|---------|--------|
| Phase 1 (done) | 21 | 139 → 118 |
| Phase 2 (pending) | ~10 | 118 → ~108 |
| Phase 3 (pending) | ~7 | ~108 → ~101 |
| **Total potential** | **~38** | **139 → ~101** |
