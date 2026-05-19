from __future__ import annotations

import json

from web_gui_mcp.render.markdown_export import export_markdown
from web_gui_mcp.schema.artifact import ArtifactSpec


def export_prompt(spec: ArtifactSpec) -> str:
    payload = json.dumps(
        spec.model_dump(mode="json", by_alias=True),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return (
        "Use this artifact as structured context for the next agent step.\n\n"
        f"{export_markdown(spec)}\n"
        "ArtifactSpec JSON:\n"
        f"```json\n{payload}\n```\n"
    )
