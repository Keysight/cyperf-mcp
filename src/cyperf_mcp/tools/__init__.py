from . import (
    agents,
    sessions,
    configs,
    test_ops,
    results,
    resources,
    controllers,
    brokers,
    licensing,
    diagnostics,
    notifications,
    statistics,
    certificates,
    system,
    migration,
)

ALL_MODULES = [
    agents,
    sessions,
    configs,
    test_ops,
    results,
    resources,
    controllers,
    brokers,
    licensing,
    diagnostics,
    notifications,
    statistics,
    certificates,
    system,
    migration,
]


def register_all(mcp, client):
    """Register all tool modules with the MCP server."""
    for module in ALL_MODULES:
        module.register(mcp, client)
