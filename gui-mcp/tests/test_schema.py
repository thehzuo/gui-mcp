from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from gui2_artifact_mcp.schema.artifact import ArtifactSpec

from .conftest import example_paths


def test_all_examples_validate() -> None:
    paths = example_paths()
    assert len(paths) == 5
    for path in paths:
        spec = ArtifactSpec.model_validate(json.loads(path.read_text(encoding="utf-8")))
        assert spec.title
        assert spec.sections


def test_unknown_section_kind_is_rejected() -> None:
    payload = {
        "v": "0.1",
        "artifact": "implementation_plan",
        "title": "Bad section",
        "sections": [{"kind": "raw_html", "html": "<script>alert(1)</script>"}],
    }
    with pytest.raises(ValidationError):
        ArtifactSpec.model_validate(payload)


def test_unknown_action_kind_is_rejected() -> None:
    payload = {
        "v": "0.1",
        "artifact": "implementation_plan",
        "title": "Bad action",
        "sections": [{"kind": "summary", "items": [{"label": "A", "value": "B"}]}],
        "actions": [{"kind": "run_javascript", "label": "Run", "script": "alert(1)"}],
    }
    with pytest.raises(ValidationError):
        ArtifactSpec.model_validate(payload)
