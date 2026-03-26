# Future Tool Reductions

Current tool count: **104** (down from 139 via Phase 1+2 consolidation + merges/removals)

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
| — | Merged `test_abort` into `test_stop(force=True)` | 1 | Done |
| 2A | Broker CRUD (5→2) → `brokers_manage` | 3 | Done |
| 2B | Licensing server CRUD (5→2) → `licensing_manage_server` | 3 | Done |
| 2C | License activate/deactivate → `licensing_activation` | 1 | Done |
| 2D | License code info → `licensing_get_code_info` | 1 | Done |
| 2E | Stats plugins (3→1) → `stats_plugins` | 2 | Done |
| — | Removed `sessions_delete_traffic_profile` / `sessions_delete_attack_profile` — auto-delete on last item removal | 2 | Done |
| — | Merged `licensing_reserve_feature` + `licensing_remove_reservation` → `licensing_reservation(action)` | 1 | Done |
| **Total saved** | | **35** | |

---

## Pending Reductions (Phase 3: Medium Risk) — ~5 tools saved

### 3A. Traffic profile tools (3→1) — 2 saved

Merge `sessions_add_applications`, `sessions_get_applications`, `sessions_remove_application` into `sessions_traffic_profile(session_id, action, ...)`.

**Risk:** Complex conditional params — `app_names` only for `add`, `app_id` only for `remove`. These tools are on the critical test setup path.

### 3B. Attack profile tools (3→1) — 2 saved

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
| Phase 2 (done) | 10 | 118 → 108 |
| Merge test_stop/abort | 1 | 108 → 107 |
| Remove profile delete tools (auto-delete) | 2 | 107 → 105 |
| Merge licensing reservation tools | 1 | 105 → 104 |
| Phase 3 (pending) | ~4 | 104 → ~100 |
| **Total potential** | **~39** | **139 → ~100** |
