from __future__ import annotations

from typing import Any

from web_gui_mcp.render.css import render_css
from web_gui_mcp.render.runtime import render_runtime_js
from web_gui_mcp.store.memory import MemoryArtifactStore

APP_MIME = "text/html;profile=mcp-app"


def runtime_css_resource() -> str:
    return render_css()


def runtime_js_resource() -> str:
    return render_runtime_js()


def artifact_resource_handler(artifact_id: str, store: MemoryArtifactStore) -> str:
    stored = store.get(artifact_id)
    if stored is None:
        raise ValueError(f"Unknown artifact_id: {artifact_id}")
    return stored.html


def register_resources(mcp: Any, store: MemoryArtifactStore) -> None:
    @mcp.resource("ui://web-gui/runtime/v0.1.css", mime_type="text/css")
    def runtime_css() -> str:
        return runtime_css_resource()

    @mcp.resource("ui://web-gui/runtime/v0.1.js", mime_type="application/javascript")
    def runtime_js() -> str:
        return runtime_js_resource()

    @mcp.resource("ui://web-gui/artifacts/{artifact_id}", mime_type=APP_MIME)
    def artifact_resource(artifact_id: str) -> str:
        return artifact_resource_handler(artifact_id, store)
