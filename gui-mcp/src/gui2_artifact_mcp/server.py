from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from gui2_artifact_mcp.mcp_resources import register_resources
from gui2_artifact_mcp.mcp_tools import register_tools
from gui2_artifact_mcp.store.memory import MemoryArtifactStore

STORE = MemoryArtifactStore()


def create_server() -> FastMCP:
    mcp = FastMCP("gui2-artifact-mcp-py")
    register_tools(mcp, STORE)
    register_resources(mcp, STORE)
    return mcp


def main() -> None:
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()
