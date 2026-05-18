from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from gui2_artifact_mcp.schema.artifact import ArtifactSpec, Density, Theme

DeliveryMode = Literal["static_html", "mcp_app", "resource_only"]
InteractivityMode = Literal["none", "local", "host_intents"]
TokenBudget = Literal["low", "medium", "rich"]


class ToolBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, serialize_by_alias=True)


class SearchArtifactPatternsInput(ToolBaseModel):
    query: str = ""
    use_case: Literal[
        "planning",
        "code_review",
        "code_understanding",
        "design",
        "design_system",
        "prototyping",
        "diagrams",
        "decks",
        "research",
        "reports",
        "editor",
    ] | None = None
    max_results: int = Field(default=5, ge=1, le=20)


class PatternSummary(ToolBaseModel):
    id: str
    name: str
    use_case: str
    description: str
    best_for: list[str]
    token_cost: Literal["low", "medium", "high"]


class SearchArtifactPatternsOutput(ToolBaseModel):
    patterns: list[PatternSummary]


class GetArtifactSchemaInput(ToolBaseModel):
    pattern_id: str
    detail: Literal["minimal", "full"] = "minimal"


class GetArtifactSchemaOutput(ToolBaseModel):
    pattern_id: str
    schema_: dict[str, Any] = Field(alias="schema")
    example_minimal: dict[str, Any]
    guidance: list[str]


class RenderOptions(ToolBaseModel):
    delivery: DeliveryMode = "resource_only"
    interactivity: InteractivityMode = "none"
    density: Density = "normal"
    theme: Theme = "neutral"
    include_runtime: bool = False
    allow_trusted_html_preview: bool = False


class RenderedArtifact(ToolBaseModel):
    artifact_id: str
    html: str
    resource_uri: str | None = None
    byte_size: int
    warnings: list[str]


class RenderArtifactInput(ToolBaseModel):
    spec: ArtifactSpec
    delivery: DeliveryMode = "resource_only"
    interactivity: InteractivityMode = "none"
    persist: bool = True
    token_budget: TokenBudget = "medium"


class RenderArtifactOutput(ToolBaseModel):
    artifact_id: str
    delivery: DeliveryMode
    title: str
    html: str | None = None
    resource_uri: str | None = None
    byte_size: int
    warnings: list[str]


class JsonPatchOp(ToolBaseModel):
    op: Literal["add", "replace", "remove"]
    path: str
    value: Any | None = None


class PatchArtifactInput(ToolBaseModel):
    artifact_id: str
    delta: list[JsonPatchOp]
    delivery: DeliveryMode = "resource_only"


class PatchArtifactOutput(RenderArtifactOutput):
    revision: int


class LintIssue(ToolBaseModel):
    check: str
    severity: Literal["info", "warning", "error"]
    message: str
    path: str | None = None


class LintArtifactInput(ToolBaseModel):
    spec: ArtifactSpec | None = None
    html: str | None = None
    checks: list[
        Literal["schema", "accessibility", "mobile", "security", "token_cost", "html_size"]
    ] = Field(default_factory=lambda: ["schema", "security", "html_size"])


class LintArtifactOutput(ToolBaseModel):
    ok: bool
    issues: list[LintIssue]


class ExportArtifactInput(ToolBaseModel):
    artifact_id: str
    format: Literal["html", "markdown", "json", "prompt"]


class ExportArtifactOutput(ToolBaseModel):
    artifact_id: str
    format: str
    content: str


class ListArtifactsInput(ToolBaseModel):
    limit: int = Field(default=20, ge=1, le=100)


class ArtifactListItem(ToolBaseModel):
    artifact_id: str
    title: str
    artifact: str
    created_at: str
    revision: int


class ListArtifactsOutput(ToolBaseModel):
    artifacts: list[ArtifactListItem]
