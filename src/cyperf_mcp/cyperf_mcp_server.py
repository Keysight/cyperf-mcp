from mcp.server.fastmcp import FastMCP
from .config import CyPerfConfig
from .client import CyPerfClientManager
from .tools import register_all

mcp = FastMCP("cyperf", json_response=True)

config = CyPerfConfig.load()
client = CyPerfClientManager(config)

register_all(mcp, client)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
