#!/usr/bin/env python3
"""CyPerf Test: Office 365 OneDrive (Simulated Users)

Creates a session from appsec-office365-onedrive-simulated-users.
This config has pre-configured IPs and is upload-heavy.
"""
from common import run_test, auto_configure_network, set_objective

CONFIG_URL = "appsec-office365-onedrive-simulated-users"
TEST_NAME = "Office 365 OneDrive (Simulated Users)"


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
