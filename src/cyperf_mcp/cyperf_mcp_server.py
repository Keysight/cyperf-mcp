import argparse
import sys
import textwrap

from mcp.server.fastmcp import FastMCP
from .config import CyPerfConfig
from .client import CyPerfClientManager
from .tools import register_all

mcp = FastMCP("cyperf", json_response=True)

config = CyPerfConfig.load()
client = CyPerfClientManager(config)

register_all(mcp, client)


def main():
    parser = argparse.ArgumentParser(
        prog="cyperf-mcp",
        description="MCP server for Keysight CyPerf network testing platform.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            configuration:
              Create a JSON config file with your CyPerf controller connection details.

              Config file location (checked in order):
                1. CYPERF_CONFIG environment variable
                2. ~/.cyperf/config.json (default)

              Single-profile shorthand:
                {
                  "host": "https://controller-ip",
                  "refresh_token": "eyJhbGciOi...",
                  "verify_ssl": false
                }

              Multi-profile format:
                {
                  "default_profile": "lab1",
                  "profiles": {
                    "lab1": { "host": "...", "refresh_token": "...", "verify_ssl": false },
                    "cloud": { "host": "...", "username": "admin", "password": "secret" }
                  }
                }

              Each profile requires:
                - host: CyPerf controller URL
                - Authentication: refresh_token OR username + password
                - verify_ssl (optional, defaults to true)

              See https://github.com/Keysight/cyperf-mcp for full documentation.
        """),
    )
    parser.parse_args()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
