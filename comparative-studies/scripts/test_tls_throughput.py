#!/usr/bin/env python3
"""CyPerf Test: TLS 1.3 Throughput

Creates a session from the TLS 1.3 throughput config (AES-256-GCM-SHA384),
configures network, runs a 300s test, and verifies sustained 10 Gbps throughput
via time-series analysis.
"""
from common import (
    create_client, get_apis, create_session, get_session, delete_session,
    auto_configure_network, set_objective, start_test, stop_test,
    wait_for_test, get_result_id, collect_all_stats, print_stat_table,
    analyze_stats, print_summary, collect_throughput_timeseries,
    print_throughput_analysis,
)

CONFIG_URL = "appsec-https-tls1.3-throughput-aws-within-vpc-c5n.9xlarge-(aes-256-gcm-sha384)"
TEST_NAME = "TLS 1.3 Throughput (AES-256-GCM-SHA384)"
TARGET_GBPS = 10.0
DURATION = 300


def main():
    print(f"\n{'='*60}")
    print(f"  {TEST_NAME}")
    print(f"{'='*60}")

    client = create_client()
    apis = get_apis(client)
    session_id = None

    try:
        # 1. Create session
        print(f"\n[1/7] Creating session from config '{CONFIG_URL}'...")
        session_id = create_session(apis["sessions"], CONFIG_URL, name=TEST_NAME)
        print(f"  Session ID: {session_id}")

        # 2. Configure
        print("\n[2/7] Configuring session...")
        session = get_session(apis["sessions"], session_id)
        auto_configure_network(session)
        set_objective(session, "THROUGHPUT", int(TARGET_GBPS), DURATION)
        print(f"  Objective: {TARGET_GBPS:.0f} Gbps throughput, {DURATION}s duration.")

        # 3. Start test
        print("\n[3/7] Starting test...")
        start_test(apis["test_ops"], session_id)

        # 4. Wait for completion
        print(f"\n[4/7] Waiting for test to complete (up to {DURATION + 60}s)...")
        status = wait_for_test(apis["sessions"], session_id, timeout=DURATION + 60)
        if status == "TIMEOUT":
            try:
                stop_test(apis["test_ops"], session_id)
            except Exception:
                pass

        # 5. Collect summary stats
        print("\n[5/7] Collecting summary statistics...")
        result_id = get_result_id(apis["sessions"], session_id)
        if not result_id:
            print("  WARNING: No result ID found.")
            return

        print(f"  Result ID: {result_id}")
        stats = collect_all_stats(apis["statistics"], result_id)
        for stat_data in stats.values():
            print_stat_table(stat_data)

        # 6. Throughput time-series analysis
        print("\n[6/7] Analyzing throughput time-series...")
        series = collect_throughput_timeseries(apis["statistics"], result_id)
        throughput_obs = print_throughput_analysis(series, TARGET_GBPS)

        # 7. Final summary
        print("\n[7/7] Final analysis...")
        observations = analyze_stats(stats)
        # Replace generic PASS with throughput-specific observations
        if throughput_obs:
            observations = [o for o in observations if not o.startswith("PASS")] + throughput_obs
        print_summary(TEST_NAME, observations)

    except Exception as e:
        print(f"\n  FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if session_id:
            print("Cleaning up...")
            delete_session(apis["sessions"], session_id)


if __name__ == "__main__":
    main()
