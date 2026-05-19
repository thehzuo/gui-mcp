from __future__ import annotations

import json
from typing import Any

from web_gui_mcp.lint.artifact import lint_artifact_input
from web_gui_mcp.registry.patterns import artifact_schema, get_pattern, search_patterns
from web_gui_mcp.render.artifact import render_artifact_to_html
from web_gui_mcp.render.markdown_export import export_markdown
from web_gui_mcp.render.prompt_export import export_prompt
from web_gui_mcp.schema.artifact import ArtifactSpec
from web_gui_mcp.schema.tool_io import (
    ArtifactListItem,
    ExportArtifactInput,
    ExportArtifactOutput,
    GetArtifactSchemaInput,
    GetArtifactSchemaOutput,
    LintArtifactInput,
    LintArtifactOutput,
    ListArtifactsInput,
    ListArtifactsOutput,
    PatchArtifactInput,
    PatchArtifactOutput,
    RenderArtifactInput,
    RenderArtifactOutput,
    RenderOptions,
    SearchArtifactPatternsInput,
    SearchArtifactPatternsOutput,
)
from web_gui_mcp.store.memory import MemoryArtifactStore
from web_gui_mcp.util.json_patch import apply_json_patch

RESOURCE_PREFIX = "ui://web-gui/artifacts"


def search_artifact_patterns_handler(
    input_data: SearchArtifactPatternsInput,
) -> SearchArtifactPatternsOutput:
    return SearchArtifactPatternsOutput(
        patterns=search_patterns(
            query=input_data.query,
            use_case=input_data.use_case,
            max_results=input_data.max_results,
        )
    )


def get_artifact_schema_handler(input_data: GetArtifactSchemaInput) -> GetArtifactSchemaOutput:
    pattern = get_pattern(input_data.pattern_id)
    return GetArtifactSchemaOutput(
        pattern_id=pattern.id,
        schema=artifact_schema(detail=input_data.detail),
        example_minimal=pattern.example_minimal,
        guidance=pattern.guidance,
    )


def render_artifact_handler(
    input_data: RenderArtifactInput,
    store: MemoryArtifactStore,
) -> RenderArtifactOutput:
    options = RenderOptions(
        delivery=input_data.delivery,
        interactivity=input_data.interactivity,
        density=input_data.spec.density,
        theme=input_data.spec.theme,
        include_runtime=input_data.interactivity != "none",
    )
    rendered = render_artifact_to_html(input_data.spec, options)
    should_store = input_data.persist or input_data.delivery in {"mcp_app", "resource_only"}
    stored = store.save(input_data.spec, rendered.html) if should_store else None
    artifact_id = stored.artifact_id if stored else rendered.artifact_id
    resource_uri = f"{RESOURCE_PREFIX}/{artifact_id}" if stored else None
    warnings = list(rendered.warnings)
    if input_data.delivery != "static_html" and not stored:
        warnings.append("No resource URI returned because persist=false.")
    if input_data.token_budget == "low" and input_data.delivery == "static_html":
        warnings.append("static_html can be token-heavy; use resource_only for low token budgets.")
    return RenderArtifactOutput(
        artifact_id=artifact_id,
        delivery=input_data.delivery,
        title=input_data.spec.title,
        html=rendered.html if input_data.delivery == "static_html" else None,
        resource_uri=resource_uri if input_data.delivery in {"mcp_app", "resource_only"} else None,
        byte_size=rendered.byte_size,
        warnings=warnings,
    )


def patch_artifact_handler(
    input_data: PatchArtifactInput,
    store: MemoryArtifactStore,
) -> PatchArtifactOutput:
    stored = store.get(input_data.artifact_id)
    if stored is None:
        raise ValueError(f"Unknown artifact_id: {input_data.artifact_id}")
    original = stored.spec.model_dump(mode="json", by_alias=True)
    patched_payload = apply_json_patch(original, input_data.delta)
    patched_spec = ArtifactSpec.model_validate(patched_payload)
    options = RenderOptions(
        delivery=input_data.delivery,
        density=patched_spec.density,
        theme=patched_spec.theme,
    )
    rendered = render_artifact_to_html(patched_spec, options)
    updated = store.replace(input_data.artifact_id, patched_spec, rendered.html)
    resource_uri = f"{RESOURCE_PREFIX}/{updated.artifact_id}"
    return PatchArtifactOutput(
        artifact_id=updated.artifact_id,
        delivery=input_data.delivery,
        title=patched_spec.title,
        html=rendered.html if input_data.delivery == "static_html" else None,
        resource_uri=resource_uri if input_data.delivery in {"mcp_app", "resource_only"} else None,
        byte_size=rendered.byte_size,
        warnings=rendered.warnings,
        revision=updated.revision,
    )


def lint_artifact_handler(input_data: LintArtifactInput) -> LintArtifactOutput:
    return lint_artifact_input(input_data)


def export_artifact_handler(
    input_data: ExportArtifactInput,
    store: MemoryArtifactStore,
) -> ExportArtifactOutput:
    stored = store.get(input_data.artifact_id)
    if stored is None:
        raise ValueError(f"Unknown artifact_id: {input_data.artifact_id}")
    if input_data.format == "html":
        content = stored.html
    elif input_data.format == "json":
        content = json.dumps(
            stored.spec.model_dump(mode="json", by_alias=True),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    elif input_data.format == "markdown":
        content = export_markdown(stored.spec)
    else:
        content = export_prompt(stored.spec)
    return ExportArtifactOutput(
        artifact_id=stored.artifact_id,
        format=input_data.format,
        content=content,
    )


def list_artifacts_handler(
    input_data: ListArtifactsInput,
    store: MemoryArtifactStore,
) -> ListArtifactsOutput:
    return ListArtifactsOutput(
        artifacts=[
            ArtifactListItem(
                artifact_id=item.artifact_id,
                title=item.spec.title,
                artifact=item.spec.artifact,
                created_at=item.created_at.isoformat(),
                revision=item.revision,
            )
            for item in store.list(limit=input_data.limit)
        ]
    )


def register_tools(mcp: Any, store: MemoryArtifactStore) -> None:
    @mcp.tool()
    def search_artifact_patterns(
        input: SearchArtifactPatternsInput,
    ) -> SearchArtifactPatternsOutput:
        return search_artifact_patterns_handler(input)

    @mcp.tool()
    def get_artifact_schema(input: GetArtifactSchemaInput) -> GetArtifactSchemaOutput:
        return get_artifact_schema_handler(input)

    @mcp.tool()
    def render_artifact(input: RenderArtifactInput) -> RenderArtifactOutput:
        return render_artifact_handler(input, store)

    @mcp.tool()
    def patch_artifact(input: PatchArtifactInput) -> PatchArtifactOutput:
        return patch_artifact_handler(input, store)

    @mcp.tool()
    def lint_artifact(input: LintArtifactInput) -> LintArtifactOutput:
        return lint_artifact_handler(input)

    @mcp.tool()
    def export_artifact(input: ExportArtifactInput) -> ExportArtifactOutput:
        return export_artifact_handler(input, store)

    @mcp.tool()
    def list_artifacts(input: ListArtifactsInput) -> ListArtifactsOutput:
        return list_artifacts_handler(input, store)
