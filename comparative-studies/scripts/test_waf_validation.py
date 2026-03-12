#!/usr/bin/env python3
"""CyPerf Test: WAF Validation (AppMix + Attacks)

Creates a session from appsec-appmix-and-attack, adds HTTP App plus
SQL Injection and XSS attacks, configures network and agents, runs
the test, and validates WAF effectiveness.
"""
from common import (
    run_test, auto_configure_network,
    set_objective, add_applications, add_attacks,
)

CONFIG_URL = "appsec-appmix-and-attack"
TEST_NAME = "WAF Validation (AppMix + Attacks)"

APPS_TO_ADD = ["HTTP App"]
ATTACKS_TO_ADD = [
    "SQL Injection Attacks",
    "XSS Attacks",
]


def configure(session, apis):
    auto_configure_network(session)

    set_objective(session, "SIMULATED_USERS", 100, 60)
    print("  Objective: 100 simulated users, 60s duration.")

    add_applications(session, apis["resources"], APPS_TO_ADD)
    print(f"  Added applications: {APPS_TO_ADD}")

    add_attacks(session, apis["resources"], ATTACKS_TO_ADD)
    print(f"  Added attacks: {ATTACKS_TO_ADD}")


if __name__ == "__main__":
    run_test(
        TEST_NAME,
        CONFIG_URL,
        configure,
        timeout=120,
    )
