#!/usr/bin/env python3
"""CyPerf Test: DDoS DNS Flood

Creates a session from appsec-ddos---dns-flood, configures network,
runs a high-volume DNS flood test, and checks for UDP drops.
"""
from common import run_test, auto_configure_network, set_objective

CONFIG_URL = "appsec-ddos---dns-flood"
TEST_NAME = "DDoS DNS Flood"


def configure(session, apis):
    auto_configure_network(session)

    set_objective(session, "SIMULATED_USERS", 100, 60)
    print("  Objective: 100 simulated users, 60s duration.")


if __name__ == "__main__":
    run_test(
        TEST_NAME,
        CONFIG_URL,
        configure,
        timeout=120,
    )
