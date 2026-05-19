from __future__ import annotations

import pytest

from web_gui_mcp.schema.artifact import ArtifactSpec
from web_gui_mcp.schema.tool_io import JsonPatchOp
from web_gui_mcp.util.json_patch import JsonPatchError, apply_json_patch


def test_json_patch_add_and_remove() -> None:
    spec = ArtifactSpec.model_validate(
        {
            "v": "0.1",
            "artifact": "implementation_plan",
            "title": "Patch",
            "sections": [{"kind": "checklist", "title": "Done", "items": [{"text": "A"}]}],
        }
    )
    payload = spec.model_dump(mode="json", by_alias=True)
    patched = apply_json_patch(
        payload,
        [
            JsonPatchOp(op="add", path="/sections/0/items/-", value={"text": "B"}),
            JsonPatchOp(op="remove", path="/sections/0/items/0"),
        ],
    )
    validated = ArtifactSpec.model_validate(patched)
    assert validated.sections[0].items[0].text == "B"  # type: ignore[attr-defined]


def test_json_patch_rejects_missing_path() -> None:
    with pytest.raises(JsonPatchError):
        apply_json_patch({"a": []}, [JsonPatchOp(op="replace", path="/a/0", value=1)])
