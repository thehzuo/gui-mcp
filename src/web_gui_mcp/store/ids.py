from __future__ import annotations

import hashlib
import json

from web_gui_mcp.schema.artifact import ArtifactSpec


def artifact_id_for_spec(spec: ArtifactSpec) -> str:
    payload = json.dumps(
        spec.model_dump(mode="json", by_alias=True),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"art_{digest}"
