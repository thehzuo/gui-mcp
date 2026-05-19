from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from gui2_artifact_mcp.schema.artifact import ArtifactSpec

from .conftest import example_paths, v01_example_paths, v02_example_paths


def test_all_examples_validate() -> None:
    paths = example_paths()
    assert len(v01_example_paths()) == 5
    assert len(v02_example_paths()) == 20
    assert len(paths) == 25
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


def test_v02_rejects_invalid_interaction_name() -> None:
    payload = {
        "v": "0.2",
        "artifact": "approach_comparison",
        "title": "Bad interaction",
        "sections": [{"kind": "summary", "items": [{"label": "A", "value": "B"}]}],
        "interactions": [{"kind": "run_script"}],
    }
    with pytest.raises(ValidationError):
        ArtifactSpec.model_validate(payload)


def test_v02_rejects_invalid_prototype_link() -> None:
    payload = {
        "v": "0.2",
        "artifact": "clickable_flow",
        "title": "Bad flow",
        "sections": [
            {
                "kind": "prototype_flow",
                "title": "Flow",
                "screens": [{"id": "a", "title": "A", "body": "A"}],
                "links": [{"from": "a", "to": "missing", "label": "Bad"}],
            }
        ],
    }
    with pytest.raises(ValidationError):
        ArtifactSpec.model_validate(payload)


def test_v02_rejects_invalid_dependency_reference() -> None:
    payload = {
        "v": "0.2",
        "artifact": "feature_flag_editor",
        "title": "Bad flags",
        "sections": [
            {
                "kind": "dependency_toggle_list",
                "title": "Flags",
                "toggles": [{"id": "retry", "label": "Retry", "depends_on": ["queue"]}],
            }
        ],
    }
    with pytest.raises(ValidationError):
        ArtifactSpec.model_validate(payload)


def test_v02_rejects_invalid_sandbox_declaration() -> None:
    payload = {
        "v": "0.2",
        "artifact": "prompt_tuner",
        "title": "Unsafe sandbox",
        "sections": [
            {
                "kind": "prompt_tuner",
                "title": "Prompt",
                "template": "Hello",
                "sandbox": {"allow_scripts": True, "allow_same_origin": True, "allow_network": False},
            }
        ],
    }
    with pytest.raises(ValidationError):
        ArtifactSpec.model_validate(payload)
