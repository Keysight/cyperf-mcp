"""Shared helpers for CyPerf standalone test scripts.

Provides client initialization, session configuration, test execution,
stats collection, and analysis utilities used by all test_*.py scripts.
"""
from __future__ import annotations

import json
import time
import sys
import warnings
from pathlib import Path

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Field name.*shadows an attribute")

import cyperf

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
AGENT_CLIENT = "1d3f9066-a9d9-49e9-a698-1efa7be52d49"  # 10.36.74.142
AGENT_SERVER = "2fc6d0bb-ea56-456b-9d3a-08b13f561558"  # 10.36.74.181

DEFAULT_CLIENT_IP = {"ip_auto": False, "ip_start": "10.0.0.10", "ip_incr": "0.0.0.1",
                     "count": 100, "max_count_per_agent": 500,
                     "gw_start": "10.0.0.1", "gw_auto": False, "net_mask": 16}
DEFAULT_SERVER_IP = {"ip_auto": False, "ip_start": "10.0.0.110", "ip_incr": "0.0.0.1",
                     "count": 1, "max_count_per_agent": 500,
                     "gw_start": "10.0.0.1", "gw_auto": False, "net_mask": 16}

# Stats IDs commonly available after a test
STAT_IDS = {
    "summary": "application-traffic-summary",
    "connections": "connection-summary",
    "throughput": "throughput-summary",
    "attacks": "attack-traffic-summary",
}

# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------

def create_client(profile_name: str | None = None) -> cyperf.ApiClient:
    """Load ~/.cyperf/config.json and return an initialized ApiClient."""
    config_path = Path.home() / ".cyperf" / "config.json"
    with open(config_path) as f:
        data = json.load(f)

    if "profiles" in data:
        name = profile_name or data.get("default_profile") or next(iter(data["profiles"]))
        profile = data["profiles"][name]
    else:
        profile = data

    cfg = cyperf.Configuration(host=profile["host"])
    cfg.verify_ssl = profile.get("verify_ssl", True)
    if "refresh_token" in profile:
        cfg.refresh_token = profile["refresh_token"]
    elif "username" in profile:
        cfg.username = profile["username"]
        cfg.password = profile["password"]

    return cyperf.ApiClient(cfg)


def get_apis(client: cyperf.ApiClient) -> dict:
    """Return a dict of all commonly needed API class instances."""
    return {
        "sessions": cyperf.SessionsApi(client),
        "test_ops": cyperf.TestOperationsApi(client),
        "resources": cyperf.ApplicationResourcesApi(client),
        "statistics": cyperf.StatisticsApi(client),
        "results": cyperf.TestResultsApi(client),
    }


# ---------------------------------------------------------------------------
# Session creation & deletion
# ---------------------------------------------------------------------------

def create_session(sessions_api: cyperf.SessionsApi, config_url: str,
                   name: str | None = None) -> str:
    """Create a session from a saved config. Returns session ID."""
    kwargs = {"config_url": config_url}
    if name:
        kwargs["name"] = name
    session = cyperf.Session(**kwargs)
    result = sessions_api.create_sessions(sessions=[session])
    # result is a list of created sessions
    if hasattr(result, '__iter__'):
        for item in result:
            if hasattr(item, 'base_model'):
                return str(item.base_model.id)
            if hasattr(item, 'id'):
                return str(item.id)
    return str(result)


def delete_session(sessions_api: cyperf.SessionsApi, session_id: str):
    """Delete a session, ignoring errors."""
    try:
        sessions_api.delete_session(session_id)
        print(f"  Session {session_id} deleted.")
    except Exception as e:
        print(f"  Warning: could not delete session {session_id}: {e}")


# ---------------------------------------------------------------------------
# Session configuration helpers
# ---------------------------------------------------------------------------

def get_session(sessions_api: cyperf.SessionsApi, session_id: str):
    """Return the DynamicModel session object."""
    return sessions_api.get_session_by_id(session_id)


def get_network_segments(session) -> list[str]:
    """Return list of network segment names."""
    names = []
    for net_profile in session.config.config.network_profiles:
        for ip_net in net_profile.ip_network_segment:
            names.append(ip_net.name)
    return names


def assign_agents(session, assignments: dict[str, list[str]]):
    """Assign agents to named network segments.

    assignments: {"Segment Name": ["agent-id-1", ...]}
    """
    for net_profile in session.config.config.network_profiles:
        for ip_net in net_profile.ip_network_segment:
            if ip_net.name not in assignments:
                continue
            agent_ids = assignments[ip_net.name]
            agent_details = [
                cyperf.AgentAssignmentDetails(agent_id=aid, id=str(idx))
                for idx, aid in enumerate(agent_ids)
            ]
            if not ip_net.agent_assignments:
                ip_net.agent_assignments = cyperf.AgentAssignments(ByID=[], ByTag=[])
            ip_net.agent_assignments.by_id = agent_details
            ip_net.update()


def disable_auto_network(session):
    """Disable ip_auto on all network segments."""
    for net_profile in session.config.config.network_profiles:
        for ip_net in net_profile.ip_network_segment:
            ip_net.ip_ranges[0].ip_auto = False
            ip_net.update()


def set_ip_range(session, segment_name: str, props: dict, ip_range_idx: int = 0):
    """Set IP range properties on a named segment."""
    for net_profile in session.config.config.network_profiles:
        for ip_net in net_profile.ip_network_segment:
            if ip_net.name == segment_name:
                ip_range = ip_net.ip_ranges[ip_range_idx]
                for key, value in props.items():
                    if hasattr(ip_range, key):
                        setattr(ip_range, key, value)
                ip_net.update()
                return
    raise ValueError(f"Segment '{segment_name}' not found")


def rename_segments(session, renames: dict[str, str]):
    """Rename network segments. renames: {old_name: new_name}."""
    for net_profile in session.config.config.network_profiles:
        for ip_net in net_profile.ip_network_segment:
            if ip_net.name in renames:
                ip_net.name = renames[ip_net.name]
                ip_net.update()


def auto_configure_network(session, *, client_ip=None, server_ip=None):
    """Auto-detect segment names, assign agents, disable auto IP, and set IPs.

    Handles any segment naming convention by using the first segment as client
    and the second as server. Uses default IPs unless overridden.
    """
    segments = get_network_segments(session)
    if len(segments) < 2:
        raise ValueError(f"Expected 2+ segments, found: {segments}")

    client_seg = segments[0]
    server_seg = segments[1]
    print(f"  Network segments: {segments}")
    print(f"  Using '{client_seg}' as client, '{server_seg}' as server.")

    assign_agents(session, {client_seg: [AGENT_CLIENT], server_seg: [AGENT_SERVER]})
    print(f"  Agents assigned.")

    disable_auto_network(session)
    set_ip_range(session, client_seg, client_ip or DEFAULT_CLIENT_IP)
    set_ip_range(session, server_seg, server_ip or DEFAULT_SERVER_IP)
    print("  Static IPs configured.")


def set_objective(session, obj_type: str = "SIMULATED_USERS",
                  obj_value: int = 100, duration: int = 60):
    """Set test objective type, value, and duration on the first traffic profile."""
    primary_objective = session.config.config.traffic_profiles[0].objectives_and_timeline.primary_objective
    primary_objective.type = getattr(cyperf.ObjectiveType, obj_type, obj_type)
    primary_objective.update()

    for segment in primary_objective.timeline:
        if segment.enabled and segment.segment_type in (
            cyperf.SegmentType.STEADYSEGMENT, cyperf.SegmentType.NORMALSEGMENT
        ):
            segment.duration = duration
            segment.objective_value = obj_value
    primary_objective.update()


def add_applications(session, resources_api: cyperf.ApplicationResourcesApi,
                     app_names: list[str], traffic_profile_idx: int = 0):
    """Add applications by exact name to the session's traffic profile."""
    if not session.config.config.traffic_profiles:
        session.config.config.traffic_profiles.append(
            cyperf.ApplicationProfile(name="Application Profile")
        )
        session.config.config.traffic_profiles.update()

    app_profile = session.config.config.traffic_profiles[traffic_profile_idx]
    for name in app_names:
        apps_result = resources_api.get_resources_apps(search_col="Name", search_val=name)
        if not len(apps_result):
            raise ValueError(f"Application '{name}' not found")
        app = None
        for candidate in apps_result:
            cname = candidate.name if hasattr(candidate, 'name') else ''
            if cname.lower() == name.lower():
                app = candidate
                break
        if app is None:
            app = apps_result[0]
        app_profile.applications.append(
            cyperf.Application(external_resource_url=app.id, objective_weight=1)
        )
    app_profile.applications.update()


def add_attacks(session, resources_api: cyperf.ApplicationResourcesApi,
                attack_names: list[str], attack_profile_idx: int = 0):
    """Add attacks by exact name to the session's attack profile."""
    if not session.config.config.attack_profiles:
        session.config.config.attack_profiles.append(
            cyperf.AttackProfile(name="Attack Profile")
        )
        session.config.config.attack_profiles.update()

    attack_profile = session.config.config.attack_profiles[attack_profile_idx]
    for name in attack_names:
        attacks_result = resources_api.get_resources_attacks(search_col="Name", search_val=name)
        if not len(attacks_result):
            raise ValueError(f"Attack '{name}' not found")
        attack = None
        for candidate in attacks_result:
            cname = candidate.name if hasattr(candidate, 'name') else ''
            if cname.lower() == name.lower():
                attack = candidate
                break
        if attack is None:
            attack = attacks_result[0]
        attack_profile.attacks.append(
            cyperf.Attack(external_resource_url=attack.id)
        )
    attack_profile.attacks.update()


# ---------------------------------------------------------------------------
# Test execution
# ---------------------------------------------------------------------------

def start_test(test_ops_api: cyperf.TestOperationsApi, session_id: str):
    """Start a test and wait for it to begin running."""
    print("  Starting test...")
    op = test_ops_api.start_test_run_start(session_id=session_id)
    op.await_completion()
    print("  Test is running.")


def stop_test(test_ops_api: cyperf.TestOperationsApi, session_id: str):
    """Stop a running test gracefully."""
    print("  Stopping test...")
    op = test_ops_api.start_test_run_stop(session_id=session_id)
    op.await_completion()
    print("  Test stopped.")


def wait_for_test(sessions_api: cyperf.SessionsApi, session_id: str,
                  timeout: int = 300, poll_interval: int = 10) -> str:
    """Poll test status until STOPPED or timeout. Returns final status."""
    elapsed = 0
    while elapsed < timeout:
        test_info = sessions_api.get_session_test(session_id)
        status = str(test_info.status) if hasattr(test_info, 'status') else str(test_info)
        if "STOPPED" in status.upper():
            print(f"  Test completed (status: {status})")
            return status
        print(f"  [{elapsed}s] Test status: {status}")
        time.sleep(poll_interval)
        elapsed += poll_interval
    print(f"  Test did not complete within {timeout}s, will stop manually.")
    return "TIMEOUT"


def get_result_id(sessions_api: cyperf.SessionsApi, session_id: str) -> str | None:
    """Get the result ID from a session's test info (stored as test_id)."""
    test_info = sessions_api.get_session_test(session_id)
    test_id = getattr(test_info, 'test_id', None)
    if test_id:
        return str(test_id)
    return None


# ---------------------------------------------------------------------------
# Stats collection & analysis
# ---------------------------------------------------------------------------

def collect_stat(statistics_api: cyperf.StatisticsApi, result_id: str,
                 stat_id: str) -> dict | None:
    """Fetch a single stat by ID, return the latest snapshot as {col: value} rows."""
    try:
        result = statistics_api.get_result_stat_by_id(result_id, stat_id)
        columns = result.columns or []
        snapshots = result.snapshots or []
        if not snapshots:
            return None
        last = snapshots[-1]
        rows = []
        for values in (last.values or []):
            row = {}
            for i, col in enumerate(columns):
                if i < len(values):
                    val = values[i]
                    if hasattr(val, 'actual_instance'):
                        val = val.actual_instance
                    row[col] = val
            rows.append(row)
        return {"name": result.name, "timestamp": last.timestamp, "data": rows}
    except Exception as e:
        print(f"  Warning: could not fetch stat '{stat_id}': {e}")
        return None


def discover_stats(statistics_api: cyperf.StatisticsApi, result_id: str) -> list[str]:
    """Discover available stat names for a result."""
    try:
        stats_list = statistics_api.get_result_stats(result_id)
        available = []
        for s in stats_list:
            sb = s.base_model if hasattr(s, 'base_model') else s
            name = getattr(sb, 'name', None) or getattr(s, 'name', None)
            if name:
                available.append(str(name))
        return available
    except Exception as e:
        print(f"  Warning: could not discover stats: {e}")
        return []


def collect_all_stats(statistics_api: cyperf.StatisticsApi, result_id: str,
                      stat_ids: list[str] | None = None) -> dict:
    """Collect multiple stats, return {stat_id: parsed_data}.

    If stat_ids is None, auto-discovers all available stats.
    """
    if stat_ids is None:
        available = discover_stats(statistics_api, result_id)
        # Filter to summary/profile stats (skip per-app and agent-metrics noise)
        INTERESTING = {"client-traffic-profile", "client-attack-profile",
                       "client-traffic-profile-tcp", "client-http-statistics",
                       "server-http-statistics", "client-latency",
                       "client-action-statistics", "client-attack-objectives"}
        stat_ids = [s for s in available if s in INTERESTING] or available[:10]
        if available:
            print(f"  Found {len(available)} stats, collecting {len(stat_ids)} key stats.")
    stats = {}
    for sid in stat_ids:
        data = collect_stat(statistics_api, result_id, sid)
        if data:
            stats[sid] = data
    return stats


def print_stat_table(stat_data: dict):
    """Pretty-print a stat's data rows as a table."""
    if not stat_data or not stat_data.get("data"):
        return
    print(f"\n  --- {stat_data['name']} ---")
    rows = stat_data["data"]
    if not rows:
        print("  (no data)")
        return
    cols = list(rows[0].keys())
    # Calculate column widths
    widths = {c: max(len(str(c)), max(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    header = " | ".join(str(c).ljust(widths[c]) for c in cols)
    print(f"  {header}")
    print(f"  {'-+-'.join('-' * widths[c] for c in cols)}")
    for row in rows:
        line = " | ".join(str(row.get(c, "")).ljust(widths[c]) for c in cols)
        print(f"  {line}")


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def collect_throughput_timeseries(statistics_api: cyperf.StatisticsApi,
                                  result_id: str,
                                  stat_name: str = "client-throughput") -> list[dict]:
    """Fetch all snapshots of a throughput stat, return list of {timestamp, bps}."""
    try:
        result = statistics_api.get_result_stat_by_id(result_id, stat_name)
        columns = result.columns or []
        snapshots = result.snapshots or []
        bps_idx = None
        for i, col in enumerate(columns):
            if "bps" in str(col).lower():
                bps_idx = i
                break
        if bps_idx is None:
            bps_idx = 1  # fallback to second column

        series = []
        for snap in snapshots:
            for values in (snap.values or []):
                val = values[bps_idx] if bps_idx < len(values) else 0
                if hasattr(val, 'actual_instance'):
                    val = val.actual_instance
                series.append({"timestamp": snap.timestamp, "bps": float(val or 0)})
        return series
    except Exception as e:
        print(f"  Warning: could not fetch throughput timeseries: {e}")
        return []


def print_throughput_analysis(series: list[dict], target_gbps: float = 10.0):
    """Print throughput time-series and check if target was sustained."""
    if not series:
        print("  No throughput data available.")
        return []

    observations = []
    gbps_values = [s["bps"] / 1e9 for s in series]
    peak = max(gbps_values)
    avg = sum(gbps_values) / len(gbps_values)

    # Find steady-state: skip first 20% (ramp-up) and last 10% (ramp-down)
    n = len(gbps_values)
    start_idx = max(1, n // 5)
    end_idx = max(start_idx + 1, n - n // 10)
    steady = gbps_values[start_idx:end_idx]
    steady_avg = sum(steady) / len(steady) if steady else 0
    steady_min = min(steady) if steady else 0

    print(f"\n  --- Throughput Time Series ({len(series)} samples) ---")
    print(f"  {'Time':>8}  {'Gbps':>8}  {'Bar'}")
    print(f"  {'--------':>8}  {'--------':>8}  {'---'}")
    t0 = series[0]["timestamp"]
    for i, s in enumerate(series):
        gbps = s["bps"] / 1e9
        elapsed = (s["timestamp"] - t0) / 1000
        bar_len = int(gbps * 4)  # 1 char per 0.25 Gbps
        marker = " <-- ramp" if (i < start_idx or i >= end_idx) else ""
        print(f"  {elapsed:7.0f}s  {gbps:8.2f}  {'#' * bar_len}{marker}")

    print(f"\n  Overall avg: {avg:.2f} Gbps | Peak: {peak:.2f} Gbps")
    print(f"  Steady-state avg: {steady_avg:.2f} Gbps | Min: {steady_min:.2f} Gbps "
          f"(samples {start_idx}-{end_idx-1} of {n})")
    print(f"  Target: {target_gbps:.1f} Gbps")

    pct = (steady_avg / target_gbps) * 100 if target_gbps > 0 else 0
    if steady_avg >= target_gbps * 0.9:
        observations.append(f"PASS: Sustained throughput {steady_avg:.2f} Gbps "
                            f"({pct:.0f}% of {target_gbps:.0f} Gbps target)")
    elif steady_avg >= target_gbps * 0.5:
        observations.append(f"WARNING: Throughput {steady_avg:.2f} Gbps is only "
                            f"{pct:.0f}% of {target_gbps:.0f} Gbps target")
    else:
        observations.append(f"ERROR: Throughput {steady_avg:.2f} Gbps is only "
                            f"{pct:.0f}% of {target_gbps:.0f} Gbps target")

    return observations


def analyze_stats(stats: dict) -> list[str]:
    """Analyze collected stats and return a list of observations."""
    observations = []

    for stat_name, stat_data in stats.items():
        rows = stat_data.get("data", [])
        for row in rows:
            # Check for failed applications/actions
            for key in row:
                kl = key.lower()
                val = _to_int(row[key])
                if val <= 0:
                    continue
                if "failed" in kl and ("app" in kl or "connection" in kl or "tcp" in kl):
                    observations.append(f"ERROR [{stat_name}]: {key} = {val}")
                elif "timed out" in kl:
                    observations.append(f"WARNING [{stat_name}]: {key} = {val}")
                elif "blocked" in kl and "strike" in kl:
                    attempted = _to_int(row.get("Strikes Attempted", 0))
                    observations.append(f"INFO [{stat_name}]: {val}/{attempted} strikes blocked")
                elif "successful" in kl and "strike" in kl:
                    attempted = _to_int(row.get("Strikes Attempted", 0))
                    observations.append(f"INFO [{stat_name}]: {val}/{attempted} strikes successful")

    if not observations:
        observations.append("PASS: No errors detected")

    return observations


def _to_int(val) -> int:
    """Safely convert a stat value to int."""
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def print_summary(test_name: str, observations: list[str]):
    """Print a formatted test summary."""
    has_error = any(o.startswith("ERROR") for o in observations)
    status = "FAIL" if has_error else "PASS"
    print(f"\n{'='*60}")
    print(f"  TEST: {test_name}")
    print(f"  STATUS: {status}")
    print(f"{'='*60}")
    for obs in observations:
        print(f"  {obs}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Script runner
# ---------------------------------------------------------------------------

def run_test(test_name: str, config_url: str, configure_fn, *,
             timeout: int = 120, stop_after: int | None = None,
             skip_objective: bool = False,
             stat_ids: list[str] | None = None):
    """Generic test runner used by all test_*.py scripts.

    Args:
        test_name: Display name for the test
        config_url: CyPerf config URL (e.g. 'appsec-123')
        configure_fn: Callback(session, apis) to customize session config
        timeout: Max seconds to wait for test completion
        stop_after: If set, stop test after this many seconds regardless
        skip_objective: If True, don't try to collect traffic-profile stats
        stat_ids: Override which stat IDs to collect
    """
    print(f"\n{'='*60}")
    print(f"  {test_name}")
    print(f"{'='*60}")

    client = create_client()
    apis = get_apis(client)
    session_id = None

    try:
        # 1. Create session
        print(f"\n[1/6] Creating session from config '{config_url}'...")
        session_id = create_session(apis["sessions"], config_url, name=test_name)
        print(f"  Session ID: {session_id}")

        # 2. Configure
        print("\n[2/6] Configuring session...")
        session = get_session(apis["sessions"], session_id)
        configure_fn(session, apis)
        print("  Configuration complete.")

        # 3. Start test
        print("\n[3/6] Starting test...")
        start_test(apis["test_ops"], session_id)

        # 4. Wait for completion
        print("\n[4/6] Waiting for test to complete...")
        if stop_after:
            print(f"  Will stop test after {stop_after}s...")
            time.sleep(stop_after)
            try:
                stop_test(apis["test_ops"], session_id)
            except Exception:
                pass  # May already be stopped
            # Give it a moment to finalize
            time.sleep(5)
        else:
            status = wait_for_test(apis["sessions"], session_id, timeout=timeout)
            if status == "TIMEOUT":
                try:
                    stop_test(apis["test_ops"], session_id)
                    time.sleep(5)
                except Exception:
                    pass

        # 5. Collect stats
        print("\n[5/6] Collecting statistics...")
        result_id = get_result_id(apis["sessions"], session_id)
        if result_id:
            print(f"  Result ID: {result_id}")
            stats = collect_all_stats(apis["statistics"], result_id, stat_ids)
            for stat_data in stats.values():
                print_stat_table(stat_data)
        else:
            print("  WARNING: No result ID found.")
            stats = {}

        # 6. Analyze & summarize
        print("\n[6/6] Analyzing results...")
        observations = analyze_stats(stats)
        print_summary(test_name, observations)

    except Exception as e:
        print(f"\n  FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        if session_id:
            print("Cleaning up...")
            delete_session(apis["sessions"], session_id)
