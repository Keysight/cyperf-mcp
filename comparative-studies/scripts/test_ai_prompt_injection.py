#!/usr/bin/env python3
"""CyPerf Test: AI Prompt Injection Attacks

Creates a session from appsec-all-dan-ai-prompt-injection-attacks.
This is an attack-only config (no traffic profile), so we skip objective
setting. The test typically completes in ~15 seconds.
"""
from common import run_test, auto_configure_network

CONFIG_URL = "appsec-all-dan-ai-prompt-injection-attacks"
TEST_NAME = "AI Prompt Injection Attacks"


def configure(session, apis):
    auto_configure_network(session)
    print("  Attack-only config — skipping objective setting.")


if __name__ == "__main__":
    run_test(
        TEST_NAME,
        CONFIG_URL,
        configure,
        timeout=60,
        skip_objective=True,
    )
