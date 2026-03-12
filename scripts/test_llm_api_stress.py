#!/usr/bin/env python3
"""CyPerf Test: LLM API Stress Test

Creates a session from appsec-276 (the saved LLM AppMix config).
This config has built-in timeline that ignores duration setting,
so we stop the test after ~130 seconds. Segments are already named
"Client Network" and "Server Network".
"""
from common import run_test, auto_configure_network

CONFIG_URL = "appsec-276"
TEST_NAME = "LLM API Stress Test"


def configure(session, apis):
    auto_configure_network(session)

    # Skip set_objective — this config's built-in timeline ignores duration
    print("  Using built-in objective/timeline (not overriding).")


if __name__ == "__main__":
    # Built-in timeline ignores duration, stop at ~130s
    run_test(
        TEST_NAME,
        CONFIG_URL,
        configure,
        timeout=180,
        stop_after=130,
    )
