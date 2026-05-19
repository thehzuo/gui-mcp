from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from web_gui_mcp.mcp_resources import register_resources
from web_gui_mcp.mcp_tools import register_tools
from web_gui_mcp.store.memory import MemoryArtifactStore

STORE = MemoryArtifactStore()


def create_server() -> FastMCP:
    mcp = FastMCP("web-gui-mcp")
    register_tools(mcp, STORE)
    register_resources(mcp, STORE)
    return mcp


def main() -> None:
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()
