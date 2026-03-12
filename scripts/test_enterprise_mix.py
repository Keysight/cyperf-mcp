#!/usr/bin/env python3
"""CyPerf Test: Enterprise Datacenter Traffic Mix

Creates a session from appsec-enterprise-datacenter-traffic-mix.
This test has long-lived sessions that may not complete within 60s,
so we stop it manually after 90 seconds.
"""
from common import run_test, auto_configure_network, set_objective

CONFIG_URL = "appsec-enterprise-datacenter-traffic-mix"
TEST_NAME = "Enterprise Datacenter Traffic Mix"


def configure(session, apis):
    auto_configure_network(session)

    set_objective(session, "SIMULATED_USERS", 100, 60)
    print("  Objective: 100 simulated users, 60s duration.")


if __name__ == "__main__":
    # Long-lived sessions may not complete in time — stop after 90s
    run_test(
        TEST_NAME,
        CONFIG_URL,
        configure,
        timeout=150,
        stop_after=90,
    )
