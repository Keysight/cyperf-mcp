# Future Tool Reductions (Medium Risk)

These are deferred consolidation opportunities that could reduce the tool count
further (~18 tools, from 132 → ~114) but carry medium risk due to complex
conditional parameter schemas that may confuse AI assistants.

---

## Approach 8: Consolidate resource browse tools (~8 tools saved)

Merge simple `list_X(take, skip)` resource tools into a single dispatcher:

**Tools to merge:**
- `resources_list_app_types`
- `resources_list_attack_categories`
- `resources_list_auth_profiles`
- `resources_list_captures`
- `resources_list_tls_certs`
- `resources_list_custom_fuzzing`
- `resources_list_payloads`
- `resources_list_pcaps`
- `resources_list_http_profiles`

**Merged into:** `resources_browse(resource_type: str, take=None, skip=None)`

Where `resource_type` is one of: `app_types`, `attack_categories`, `auth_profiles`,
`captures`, `tls_certs`, `custom_fuzzing`, `payloads`, `pcaps`, `http_profiles`.

Keep `resources_list_apps` and `resources_list_attacks` separate (they have search params).

**Risk:** Dispatch logic; parameter schema becomes less discoverable for the AI.

---

## Approach 9: Merge profile management tools (~6 tools saved)

**Traffic profile apps (4 → 1):**
- `sessions_add_applications`
- `sessions_get_applications`
- `sessions_remove_application`
- `sessions_delete_traffic_profile`

→ `sessions_traffic_profile(session_id, action="list"|"add"|"remove"|"delete", ...)`

**Attack profile (4 → 1):**
- `sessions_add_attacks`
- `sessions_get_attacks`
- `sessions_remove_attack`
- `sessions_delete_attack_profile`

→ `sessions_attack_profile(session_id, action="list"|"add"|"remove"|"delete", ...)`

**Risk:** Complex conditional parameter schema — `app_names` only for "add",
`app_id` only for "remove", `traffic_profile_id` always needed. AI may struggle
with the right parameter combination per action.

---

## Approach 10: Merge licensing server CRUD (~4 tools saved)

**Tools to merge:**
- `licensing_list_servers`
- `licensing_add_server`
- `licensing_get_server`
- `licensing_update_server`
- `licensing_delete_server`

→ `licensing_server(action="list"|"get"|"add"|"update"|"delete", server_id=None, ...)`

**Risk:** Same conditional parameter complexity — `server_id` required for
get/update/delete but not list/add; server data only for add/update.

---

## Summary

| Approach | Savings | Current tools affected |
|----------|---------|----------------------|
| 8. Consolidate resource browse | ~8 | resources.py |
| 9. Merge profile management | ~6 | sessions.py |
| 10. Merge licensing server CRUD | ~4 | licensing.py |
| **Total** | **~18** | **132 → ~114** |
