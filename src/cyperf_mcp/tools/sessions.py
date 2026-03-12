from __future__ import annotations

from difflib import SequenceMatcher

import cyperf
from ..client import CyPerfClientManager
from ..helpers import serialize_response, handle_api_error, handle_exception, await_and_serialize, build_list_kwargs


def _best_match(query: str, candidates):
    """Return the candidate with the best name match for *query*.

    Exact (case-insensitive) match wins outright.  Otherwise the candidate
    whose name is most similar to the query (by SequenceMatcher ratio) is
    returned, so "Microsoft Teams Attendee - Audio Call" will prefer
    "Microsoft Teams Attendee - Audio Meeting" over an unrelated Teams app.
    """
    query_lower = query.lower()
    best, best_score = None, -1.0
    for c in candidates:
        cname = c.name if hasattr(c, 'name') else ''
        cname_lower = cname.lower()
        if cname_lower == query_lower:
            return c                       # exact match – done
        score = SequenceMatcher(None, query_lower, cname_lower).ratio()
        if score > best_score:
            best, best_score = c, score
    return best if best is not None else candidates[0]


class SessionTools:
    """Session management tools for CyPerf MCP server."""

    def __init__(self, client: CyPerfClientManager):
        self._client = client

    @property
    def api(self) -> cyperf.SessionsApi:
        return self._client.sessions

    def list(self, take=None, skip=None, search_col=None, search_val=None,
             filter_mode=None, sort=None):
        try:
            kwargs = build_list_kwargs(take, skip, search_col, search_val, filter_mode, sort)
            result = self.api.get_sessions(**kwargs)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def create(self, session_data: dict):
        try:
            session = cyperf.Session(**session_data)
            result = self.api.create_sessions(sessions=[session])
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get(self, session_id: str):
        try:
            result = self.api.get_session_by_id(session_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete(self, session_id: str):
        """Delete a session. Stops the test first if it's running (mirrors utils.delete_session)."""
        try:
            test = self.api.get_session_test(session_id=session_id)
            if test.status != 'STOPPED':
                test_ops = self._client.test_ops
                stop_op = test_ops.start_test_run_stop(session_id=session_id)
                stop_op.await_completion()
            self.api.delete_session(session_id)
            return {"result": f"Session {session_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def update(self, session_id: str, properties: dict):
        try:
            session = cyperf.Session(**properties)
            result = self.api.patch_session(session_id, session=session)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def batch_delete(self, session_ids: list[str]):
        try:
            results = []
            for sid in session_ids:
                self.api.delete_session(sid)
                results.append(sid)
            return {"result": f"Deleted {len(results)} sessions", "deleted": results}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_config(self, session_id: str):
        try:
            result = self.api.get_session_config(session_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def save_config(self, session_id: str, name: str = None):
        try:
            if name:
                op = cyperf.SaveConfigOperation(name=name)
                result = self.api.start_session_config_save(session_id, save_config_operation=op)
            else:
                result = self.api.start_session_config_save(session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def load_config(self, session_id: str, config_url: str):
        try:
            op = cyperf.LoadConfigOperationInput(config_url=config_url)
            result = self.api.start_session_load_config(session_id, operation=op)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_meta(self, session_id: str):
        try:
            result = self.api.get_session_meta(session_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_test(self, session_id: str):
        try:
            result = self.api.get_session_test(session_id)
            return serialize_response(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def touch(self, session_id: str):
        try:
            result = self.api.start_session_touch(session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def add_applications(self, session_id: str, traffic_profile_id: str,
                         app_names: list[str]):
        """Look up apps by name, then add them to the traffic profile via DynamicModel."""
        try:
            resources_api = self._client.resources
            session = self.api.get_session_by_id(session_id)

            if not session.config.config.traffic_profiles:
                session.config.config.traffic_profiles.append(
                    cyperf.ApplicationProfile(name="Application Profile")
                )
                session.config.config.traffic_profiles.update()

            app_profile = session.config.config.traffic_profiles[
                int(traffic_profile_id) - 1
            ]

            added = []
            skipped = []
            for name in app_names:
                apps_result = resources_api.get_resources_apps(
                    search_col="Name", search_val=name
                )
                if not len(apps_result):
                    return {"error": True, "message": f"Application '{name}' not found"}
                app = _best_match(name, apps_result)
                matched_name = app.name if hasattr(app, 'name') else str(app.id)
                # Validate the resource URL exists before adding
                try:
                    resources_api.get_resources_apps_by_id(app.id)
                except Exception:
                    skipped.append({
                        "name": name, "matched": matched_name,
                        "reason": f"Resource id={app.id} not found on server (404)"
                    })
                    continue
                app_profile.applications.append(
                    cyperf.Application(
                        external_resource_url=app.id, objective_weight=1
                    )
                )
                added.append(matched_name)

            app_profile.applications.update()
            result = {"result": "completed", "applications_added": added}
            if skipped:
                result["skipped"] = skipped
            return result
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def add_attacks(self, session_id: str, attack_profile_id: str,
                    attack_names: list[str]):
        """Look up attacks by name, then add them to the attack profile via DynamicModel."""
        try:
            resources_api = self._client.resources
            session = self.api.get_session_by_id(session_id)

            if not session.config.config.attack_profiles:
                session.config.config.attack_profiles.append(
                    cyperf.AttackProfile(name="Attack Profile")
                )
                session.config.config.attack_profiles.update()

            attack_profile = session.config.config.attack_profiles[
                int(attack_profile_id) - 1
            ]

            added = []
            skipped = []
            for name in attack_names:
                attacks_result = resources_api.get_resources_attacks(
                    search_col="Name", search_val=name
                )
                if not len(attacks_result):
                    return {"error": True, "message": f"Attack '{name}' not found"}
                attack = _best_match(name, attacks_result)
                matched_name = attack.name if hasattr(attack, 'name') else str(attack.id)
                # Validate the resource URL exists before adding
                try:
                    resources_api.get_resources_attacks_by_id(attack.id)
                except Exception:
                    skipped.append({
                        "name": name, "matched": matched_name,
                        "reason": f"Resource id={attack.id} not found on server (404)"
                    })
                    continue
                attack_profile.attacks.append(
                    cyperf.Attack(external_resource_url=attack.id)
                )
                added.append(matched_name)

            attack_profile.attacks.update()
            result = {"result": "completed", "attacks_added": added}
            if skipped:
                result["skipped"] = skipped
            return result
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_traffic_profile_applications(self, session_id: str,
                                            traffic_profile_id: str = "1"):
        """List applications in a session's traffic profile via DynamicModel."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(traffic_profile_id) - 1
            if not session.config.config.traffic_profiles or idx >= len(session.config.config.traffic_profiles):
                return {"data": []}
            app_profile = session.config.config.traffic_profiles[idx]
            apps = []
            for app in app_profile.applications:
                bm = app.base_model
                apps.append({
                    "Name": getattr(bm, 'name', None),
                    "id": getattr(bm, 'id', None),
                    "Active": getattr(bm, 'active', None),
                    "ExternalResourceURL": getattr(bm, 'external_resource_url', None),
                })
            return {"data": apps}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_attack_profile_attacks(self, session_id: str,
                                   attack_profile_id: str = "1"):
        """List attacks in a session's attack profile via DynamicModel."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(attack_profile_id) - 1
            if not session.config.config.attack_profiles or idx >= len(session.config.config.attack_profiles):
                return {"data": []}
            attack_profile = session.config.config.attack_profiles[idx]
            attacks = []
            for attack in attack_profile.attacks:
                bm = attack.base_model
                attacks.append({
                    "Name": getattr(bm, 'name', None),
                    "id": getattr(bm, 'id', None),
                    "Active": getattr(bm, 'active', None),
                })
            return {"data": attacks}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_app_actions(self, session_id: str, traffic_profile_id: str = "1",
                        app_id: str = None):
        """List actions for an application in a session's traffic profile."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(traffic_profile_id) - 1
            if not session.config.config.traffic_profiles or idx >= len(session.config.config.traffic_profiles):
                return {"error": True, "message": f"Traffic profile {traffic_profile_id} not found"}
            app_profile = session.config.config.traffic_profiles[idx]
            for app in app_profile.applications:
                if str(app.base_model.id) == str(app_id):
                    actions = []
                    for track in app.tracks:
                        for action in track.actions:
                            bm = action.base_model
                            params = []
                            for param in action.params:
                                pbm = param.base_model
                                params.append({
                                    "name": getattr(pbm, 'name', None),
                                    "id": getattr(pbm, 'id', None),
                                    "value": getattr(pbm, 'value', None),
                                })
                            actions.append({
                                "name": getattr(bm, 'name', None),
                                "id": getattr(bm, 'id', None),
                                "params": params,
                            })
                    return {"app_name": app.base_model.name, "app_id": app_id, "actions": actions}
            return {"error": True, "message": f"Application with id={app_id} not found"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_app_action_param(self, session_id: str, traffic_profile_id: str = "1",
                             app_id: str = None, action_id: str = None,
                             param_id: str = None, value: str = None):
        """Set the value of an action parameter."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(traffic_profile_id) - 1
            if not session.config.config.traffic_profiles or idx >= len(session.config.config.traffic_profiles):
                return {"error": True, "message": f"Traffic profile {traffic_profile_id} not found"}
            app_profile = session.config.config.traffic_profiles[idx]
            for app in app_profile.applications:
                if str(app.base_model.id) == str(app_id):
                    for track in app.tracks:
                        for action in track.actions:
                            if str(action.base_model.id) == str(action_id):
                                for param in action.params:
                                    if str(param.base_model.id) == str(param_id):
                                        old_value = param.base_model.value
                                        param.base_model.value = value
                                        action.update()
                                        return {
                                            "result": f"Parameter '{param.base_model.name}' updated",
                                            "old_value": old_value,
                                            "new_value": value,
                                        }
                                return {"error": True, "message": f"Param id={param_id} not found in action {action_id}"}
                    return {"error": True, "message": f"Action id={action_id} not found in app {app_id}"}
            return {"error": True, "message": f"Application with id={app_id} not found"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def remove_app_action(self, session_id: str, traffic_profile_id: str = "1",
                          app_id: str = None, action_id: str = None):
        """Remove an action by ID from an application in a session's traffic profile."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(traffic_profile_id) - 1
            if not session.config.config.traffic_profiles or idx >= len(session.config.config.traffic_profiles):
                return {"error": True, "message": f"Traffic profile {traffic_profile_id} not found"}
            app_profile = session.config.config.traffic_profiles[idx]
            for app in app_profile.applications:
                if str(app.base_model.id) == str(app_id):
                    for track in app.tracks:
                        for action in track.actions:
                            if str(action.base_model.id) == str(action_id):
                                action_name = getattr(action.base_model, 'name', action_id)
                                action.delete()
                                return {"result": f"Action '{action_name}' (id={action_id}) removed from '{app.base_model.name}'"}
                    return {"error": True, "message": f"Action with id={action_id} not found in app {app_id}"}
            return {"error": True, "message": f"Application with id={app_id} not found"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def remove_application(self, session_id: str, traffic_profile_id: str = "1",
                            app_id: str = None):
        """Remove an application by its ID from a session's traffic profile."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(traffic_profile_id) - 1
            if not session.config.config.traffic_profiles or idx >= len(session.config.config.traffic_profiles):
                return {"error": True, "message": f"Traffic profile {traffic_profile_id} not found"}
            app_profile = session.config.config.traffic_profiles[idx]
            for i, app in enumerate(app_profile.applications):
                if str(app.base_model.id) == str(app_id):
                    removed_name = getattr(app.base_model, 'name', app_id)
                    app.delete()
                    return {"result": f"Application '{removed_name}' (id={app_id}) removed"}
            return {"error": True, "message": f"Application with id={app_id} not found in traffic profile"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def remove_attack(self, session_id: str, attack_profile_id: str = "1",
                      attack_id: str = None):
        """Remove an attack by its ID from a session's attack profile."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(attack_profile_id) - 1
            if not session.config.config.attack_profiles or idx >= len(session.config.config.attack_profiles):
                return {"error": True, "message": f"Attack profile {attack_profile_id} not found"}
            attack_profile = session.config.config.attack_profiles[idx]
            for i, attack in enumerate(attack_profile.attacks):
                if str(attack.base_model.id) == str(attack_id):
                    removed_name = getattr(attack.base_model, 'name', attack_id)
                    attack.delete()
                    return {"result": f"Attack '{removed_name}' (id={attack_id}) removed"}
            return {"error": True, "message": f"Attack with id={attack_id} not found in attack profile"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete_traffic_profile(self, session_id: str, traffic_profile_id: str = "1"):
        """Delete a traffic/application profile from a session via DynamicModel.delete()."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(traffic_profile_id) - 1
            if not session.config.config.traffic_profiles or idx >= len(session.config.config.traffic_profiles):
                return {"error": True, "message": f"Traffic profile {traffic_profile_id} not found"}
            traffic_profile = session.config.config.traffic_profiles[idx]
            traffic_profile.delete()
            return {"result": f"Traffic profile {traffic_profile_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def delete_attack_profile(self, session_id: str, attack_profile_id: str = "1"):
        """Delete an attack profile from a session via DynamicModel.delete()."""
        try:
            session = self.api.get_session_by_id(session_id)
            idx = int(attack_profile_id) - 1
            if not session.config.config.attack_profiles or idx >= len(session.config.config.attack_profiles):
                return {"error": True, "message": f"Attack profile {attack_profile_id} not found"}
            attack_profile = session.config.config.attack_profiles[idx]
            attack_profile.delete()
            return {"result": f"Attack profile {attack_profile_id} deleted"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def assign_agents(self, session_id: str, agent_assignments: dict):
        """Assign agents to network segments via DynamicModel (mirrors utils.assign_agents)."""
        try:
            session = self.api.get_session_by_id(session_id)
            assigned = {}
            available_segments = []
            for net_profile in session.config.config.network_profiles:
                for ip_net in net_profile.ip_network_segment:
                    available_segments.append(ip_net.name)
                    if ip_net.name not in agent_assignments:
                        continue
                    agent_ids = agent_assignments[ip_net.name]
                    agent_details = [
                        cyperf.AgentAssignmentDetails(agent_id=aid, id=str(idx))
                        for idx, aid in enumerate(agent_ids)
                    ]
                    if not ip_net.agent_assignments:
                        ip_net.agent_assignments = cyperf.AgentAssignments(ByID=[], ByTag=[])
                    ip_net.agent_assignments.by_id = agent_details
                    ip_net.update()
                    assigned[ip_net.name] = agent_ids
            result = {"result": "Agents assigned", "assignments": assigned,
                      "available_segments": available_segments}
            if not assigned:
                result["warning"] = "No segments matched. Check available_segments for valid names."
            return result
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def rename_network_segments(self, session_id: str, renames: dict):
        """Rename network segments. renames maps old name to new name."""
        try:
            session = self.api.get_session_by_id(session_id)
            renamed = {}
            available_segments = []
            for net_profile in session.config.config.network_profiles:
                for ip_net in net_profile.ip_network_segment:
                    available_segments.append(ip_net.name)
                    if ip_net.name in renames:
                        old_name = ip_net.name
                        ip_net.name = renames[old_name]
                        ip_net.update()
                        renamed[old_name] = renames[old_name]
            result = {"result": "Segments renamed", "renamed": renamed,
                      "available_segments": available_segments}
            if not renamed:
                result["warning"] = "No segments matched. Check available_segments for valid names."
            return result
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def get_network_segments(self, session_id: str):
        """List network segments with their IP range settings."""
        try:
            session = self.api.get_session_by_id(session_id)
            segments = []
            for net_profile in session.config.config.network_profiles:
                for ip_net in net_profile.ip_network_segment:
                    ip_ranges = []
                    for ip_range in ip_net.ip_ranges:
                        bm = ip_range.base_model
                        ip_ranges.append({
                            "id": getattr(bm, 'id', None),
                            "ip_auto": getattr(bm, 'ip_auto', None),
                            "ip_start": getattr(bm, 'ip_start', None),
                            "ip_incr": getattr(bm, 'ip_incr', None),
                            "count": getattr(bm, 'count', None),
                            "max_count_per_agent": getattr(bm, 'max_count_per_agent', None),
                            "gw_start": getattr(bm, 'gw_start', None),
                            "gw_auto": getattr(bm, 'gw_auto', None),
                            "net_mask": getattr(bm, 'net_mask', None),
                            "ip_ver": getattr(bm, 'ip_ver', None),
                        })
                    segments.append({
                        "name": ip_net.name,
                        "ip_ranges": ip_ranges,
                    })
            return {"data": segments}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_network_ip_range(self, session_id: str, segment_name: str, ip_range_id: str = "1",
                             properties: dict = None):
        """Update IP range properties on a network segment by name."""
        try:
            session = self.api.get_session_by_id(session_id)
            for net_profile in session.config.config.network_profiles:
                for ip_net in net_profile.ip_network_segment:
                    if ip_net.name == segment_name:
                        idx = int(ip_range_id) - 1
                        if idx >= len(ip_net.ip_ranges):
                            return {"error": True, "message": f"IP range {ip_range_id} not found"}
                        ip_range = ip_net.ip_ranges[idx]
                        updated = {}
                        for key, value in (properties or {}).items():
                            if hasattr(ip_range, key):
                                setattr(ip_range, key, value)
                                updated[key] = value
                        ip_net.update()
                        return {"result": f"IP range updated on '{segment_name}'", "updated": updated}
            available = []
            for net_profile in session.config.config.network_profiles:
                for ip_net in net_profile.ip_network_segment:
                    available.append(ip_net.name)
            return {"error": True, "message": f"Segment '{segment_name}' not found",
                    "available_segments": available}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def disable_automatic_network(self, session_id: str):
        """Disable automatic IP on all network segments (mirrors utils.disable_automatic_network)."""
        try:
            session = self.api.get_session_by_id(session_id)
            for net_profile in session.config.config.network_profiles:
                for ip_net in net_profile.ip_network_segment:
                    ip_net.ip_ranges[0].ip_auto = False
                    ip_net.update()
            return {"result": "Automatic network disabled"}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def set_objective_and_timeline(self, session_id: str, objective_type: str = "SIMULATED_USERS",
                                   objective_value: int = 100, duration: int = 600):
        """Set test objective and timeline via DynamicModel (mirrors utils.set_objective_and_timeline)."""
        try:
            session = self.api.get_session_by_id(session_id)
            primary_objective = session.config.config.traffic_profiles[0].objectives_and_timeline.primary_objective
            primary_objective.type = getattr(cyperf.ObjectiveType, objective_type, objective_type)
            primary_objective.update()

            for segment in primary_objective.timeline:
                if segment.enabled and segment.segment_type in (
                    cyperf.SegmentType.STEADYSEGMENT, cyperf.SegmentType.NORMALSEGMENT
                ):
                    segment.duration = duration
                    segment.objective_value = objective_value
            primary_objective.update()
            return {"result": "Objective and timeline updated",
                    "type": objective_type, "value": objective_value, "duration": duration}
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def test_init(self, session_id: str):
        try:
            result = self.api.start_session_test_init(session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def test_end(self, session_id: str):
        try:
            result = self.api.start_session_test_end(session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)

    def prepare_test(self, session_id: str):
        try:
            result = self.api.start_session_prepare_test(session_id)
            return await_and_serialize(result)
        except cyperf.ApiException as e:
            return handle_api_error(e)
        except Exception as e:
            return handle_exception(e)


def register(mcp, client: CyPerfClientManager):
    """Register all session tools with the MCP server."""
    tools = SessionTools(client)

    @mcp.tool()
    def sessions_list(take: int = None, skip: int = None,
                      search_col: str = None, search_val: str = None,
                      filter_mode: str = None, sort: str = None) -> dict:
        """[Sessions] List all CyPerf sessions with optional filtering and search.

        Args:
            take: Number of results to return
            skip: Number of results to skip
            search_col: Column to search (e.g. 'name')
            search_val: Value to search for
            filter_mode: Filter mode ('contains', 'exact', etc.)
            sort: Sort expression
        """
        return tools.list(take, skip, search_col, search_val, filter_mode, sort)

    @mcp.tool()
    def sessions_create(session_data: dict) -> dict:
        """[Sessions] Create a new CyPerf session.

        Args:
            session_data: Session properties. Must include 'config_url' pointing to
                          a saved configuration (e.g. 'appsec-123' from configs_list).
                          Optional: 'name' for a display name.
        """
        return tools.create(session_data)

    @mcp.tool()
    def sessions_get(session_id: str) -> dict:
        """[Sessions] Get details of a specific session by ID.

        Args:
            session_id: The session identifier
        """
        return tools.get(session_id)

    @mcp.tool()
    def sessions_delete(session_ids: list[str]) -> dict:
        """[Sessions] Delete one or more sessions. Stops running tests first.

        Args:
            session_ids: List of session IDs to delete (single or multiple)
        """
        if len(session_ids) == 1:
            return tools.delete(session_ids[0])
        return tools.batch_delete(session_ids)

    @mcp.tool()
    def sessions_update(session_id: str, properties: dict) -> dict:
        """[Sessions] Update session properties.

        Args:
            session_id: The session identifier
            properties: Dict of session properties to update
        """
        return tools.update(session_id, properties)

    @mcp.tool()
    def sessions_get_config(session_id: str) -> dict:
        """[Sessions] Get the configuration of a session.

        Args:
            session_id: The session identifier
        """
        return tools.get_config(session_id)

    @mcp.tool()
    def sessions_save_config(session_id: str, name: str = None) -> dict:
        """[Sessions] Save session configuration persistently.

        Args:
            session_id: The session identifier
            name: Optional new name for the configuration before saving
        """
        return tools.save_config(session_id, name)

    @mcp.tool()
    def sessions_load_config(session_id: str, config_url: str) -> dict:
        """[Sessions] Load a configuration into a session.

        Args:
            session_id: The session identifier
            config_url: URL or path of the configuration to load
        """
        return tools.load_config(session_id, config_url)

    @mcp.tool()
    def sessions_get_meta(session_id: str) -> dict:
        """[Sessions] Get session metadata.

        Args:
            session_id: The session identifier
        """
        return tools.get_meta(session_id)

    @mcp.tool()
    def sessions_get_test(session_id: str) -> dict:
        """[Sessions] Get session test info (status, progress, etc.).

        Args:
            session_id: The session identifier
        """
        return tools.get_test(session_id)

    @mcp.tool()
    def sessions_touch(session_id: str) -> dict:
        """[Sessions] Keep a session alive (heartbeat).

        Args:
            session_id: The session identifier
        """
        return tools.touch(session_id)

    @mcp.tool()
    def sessions_add_applications(session_id: str, traffic_profile_id: str,
                                  app_names: list[str]) -> dict:
        """[Sessions] Add applications by name to a session's traffic profile.

        Looks up each application by name (exact match preferred, falls back to
        substring match). Use resources_search_apps or resources_list_apps to
        discover available names first. Use exact names like 'HTTP App' not 'HTTP'.

        Args:
            session_id: The session identifier
            traffic_profile_id: The traffic profile ID within the session config
            app_names: List of exact application names to add (e.g. ['HTTP App', 'HTTPS'])
        """
        return tools.add_applications(session_id, traffic_profile_id, app_names)

    @mcp.tool()
    def sessions_add_attacks(session_id: str, attack_profile_id: str,
                             attack_names: list[str]) -> dict:
        """[Sessions] Add attacks by name to a session's attack profile.

        Looks up each attack by name (exact match preferred, falls back to
        substring match). Use resources_search_attacks or resources_list_attacks
        to discover available names first. Use exact names.

        Args:
            session_id: The session identifier
            attack_profile_id: The attack profile ID within the session config
            attack_names: List of exact attack names to add
        """
        return tools.add_attacks(session_id, attack_profile_id, attack_names)

    @mcp.tool()
    def sessions_get_applications(session_id: str,
                                  traffic_profile_id: str = "1") -> dict:
        """[Sessions] List applications in a session's traffic profile.

        Args:
            session_id: The session identifier
            traffic_profile_id: The traffic profile ID (default '1')
        """
        return tools.get_traffic_profile_applications(session_id,
                                                      traffic_profile_id)

    @mcp.tool()
    def sessions_get_attacks(session_id: str,
                             attack_profile_id: str = "1") -> dict:
        """[Sessions] List attacks in a session's attack profile.

        Args:
            session_id: The session identifier
            attack_profile_id: The attack profile ID (default '1')
        """
        return tools.get_attack_profile_attacks(session_id, attack_profile_id)

    @mcp.tool()
    def sessions_get_app_actions(session_id: str, traffic_profile_id: str = "1",
                                  app_id: str = None) -> dict:
        """[Sessions] List actions for an application in a session's traffic profile.

        Args:
            session_id: The session identifier
            traffic_profile_id: The traffic profile ID (default '1')
            app_id: The application ID within the traffic profile
        """
        return tools.get_app_actions(session_id, traffic_profile_id, app_id)

    @mcp.tool()
    def sessions_remove_app_action(session_id: str, traffic_profile_id: str = "1",
                                    app_id: str = None, action_id: str = None) -> dict:
        """[Sessions] Remove an action from an application in a session's traffic profile.

        Use sessions_get_app_actions to find the action ID first.

        Args:
            session_id: The session identifier
            traffic_profile_id: The traffic profile ID (default '1')
            app_id: The application ID within the traffic profile
            action_id: The action ID to remove
        """
        return tools.remove_app_action(session_id, traffic_profile_id, app_id, action_id)

    @mcp.tool()
    def sessions_set_app_action_param(session_id: str, traffic_profile_id: str = "1",
                                       app_id: str = None, action_id: str = None,
                                       param_id: str = None, value: str = None) -> dict:
        """[Sessions] Set the value of an action parameter in an application.

        Use sessions_get_app_actions to find app_id, action_id, and param_id first.

        Args:
            session_id: The session identifier
            traffic_profile_id: The traffic profile ID (default '1')
            app_id: The application ID within the traffic profile
            action_id: The action ID within the application
            param_id: The parameter ID within the action
            value: The new value for the parameter
        """
        return tools.set_app_action_param(session_id, traffic_profile_id,
                                           app_id, action_id, param_id, value)

    @mcp.tool()
    def sessions_remove_application(session_id: str, traffic_profile_id: str = "1",
                                     app_id: str = None) -> dict:
        """[Sessions] Remove an application from a session's traffic profile by app ID.

        Use sessions_get_applications to find the app ID first.

        Args:
            session_id: The session identifier
            traffic_profile_id: The traffic profile ID (default '1')
            app_id: The application ID within the traffic profile to remove
        """
        return tools.remove_application(session_id, traffic_profile_id, app_id)

    @mcp.tool()
    def sessions_remove_attack(session_id: str, attack_profile_id: str = "1",
                                attack_id: str = None) -> dict:
        """[Sessions] Remove an attack from a session's attack profile by attack ID.

        Use sessions_get_attacks to find the attack ID first.

        Args:
            session_id: The session identifier
            attack_profile_id: The attack profile ID (default '1')
            attack_id: The attack ID within the attack profile to remove
        """
        return tools.remove_attack(session_id, attack_profile_id, attack_id)

    @mcp.tool()
    def sessions_delete_attack_profile(session_id: str,
                                       attack_profile_id: str = "1") -> dict:
        """[Sessions] Delete an attack profile from a session.

        Args:
            session_id: The session identifier
            attack_profile_id: The attack profile ID to delete (default '1')
        """
        return tools.delete_attack_profile(session_id, attack_profile_id)

    @mcp.tool()
    def sessions_delete_traffic_profile(session_id: str,
                                        traffic_profile_id: str = "1") -> dict:
        """[Sessions] Delete a traffic/application profile from a session.

        Args:
            session_id: The session identifier
            traffic_profile_id: The traffic profile ID to delete (default '1')
        """
        return tools.delete_traffic_profile(session_id, traffic_profile_id)

    @mcp.tool()
    def sessions_assign_agents(session_id: str, agent_assignments: dict) -> dict:
        """[Sessions] Assign agents to network segments in a session.

        Uses DynamicModel to assign agents by ID to named network segments.

        Args:
            session_id: The session identifier
            agent_assignments: Dict mapping segment name to list of agent IDs.
                              E.g. {"Client": ["agent-id-1"], "Server": ["agent-id-2"]}
        """
        return tools.assign_agents(session_id, agent_assignments)

    @mcp.tool()
    def sessions_rename_network_segments(session_id: str, renames: dict) -> dict:
        """[Sessions] Rename network segments in a session.

        Args:
            session_id: The session identifier
            renames: Dict mapping old segment name to new name.
                     E.g. {"IP Network 1": "Client Network", "IP Network 2": "Server Network"}
        """
        return tools.rename_network_segments(session_id, renames)

    @mcp.tool()
    def sessions_get_network_segments(session_id: str) -> dict:
        """[Sessions] List network segments with their IP range settings.

        Args:
            session_id: The session identifier
        """
        return tools.get_network_segments(session_id)

    @mcp.tool()
    def sessions_set_network_ip_range(session_id: str, segment_name: str,
                                       ip_range_id: str = "1",
                                       properties: dict = None) -> dict:
        """[Sessions] Update IP range properties on a network segment.

        Use sessions_get_network_segments to see current values first.

        Args:
            session_id: The session identifier
            segment_name: The network segment name (e.g. 'Client Network')
            ip_range_id: The IP range ID within the segment (default '1')
            properties: Dict of properties to update. Valid keys include:
                        ip_auto, ip_start, ip_incr, count, max_count_per_agent,
                        gw_start, gw_auto, net_mask, net_mask_auto
        """
        return tools.set_network_ip_range(session_id, segment_name, ip_range_id, properties)

    @mcp.tool()
    def sessions_disable_automatic_network(session_id: str) -> dict:
        """[Sessions] Disable automatic IP assignment on all network segments.

        Args:
            session_id: The session identifier
        """
        return tools.disable_automatic_network(session_id)

    @mcp.tool()
    def sessions_set_objective_and_timeline(session_id: str,
                                            objective_type: str = "SIMULATED_USERS",
                                            objective_value: int = 100,
                                            duration: int = 600) -> dict:
        """[Sessions] Set test objective type, value, and duration.

        Args:
            session_id: The session identifier
            objective_type: Objective type (e.g. 'SIMULATED_USERS', 'THROUGHPUT')
            objective_value: Target value for the objective
            duration: Test duration in seconds
        """
        return tools.set_objective_and_timeline(session_id, objective_type,
                                                objective_value, duration)

    # Note: test_init, test_end, prepare_test are available via test_ops tools
    # (test_init, test_end, test_prepare) to avoid duplication.
