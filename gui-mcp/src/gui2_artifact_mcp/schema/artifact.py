from __future__ import annotations

from typing import Annotated, Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from gui2_artifact_mcp.schema.limits import (
    MAX_ACTIONS,
    MAX_BODY_LENGTH,
    MAX_CODE_LENGTH,
    MAX_COLUMNS,
    MAX_ROWS,
    MAX_SECTIONS,
    MAX_SOURCES,
    MAX_TITLE_LENGTH,
)

Tone: TypeAlias = Literal["neutral", "good", "warning", "danger", "info"]
Audience: TypeAlias = Literal["self", "team", "executive", "reviewer"]
Density: TypeAlias = Literal["compact", "normal", "presentation"]
Theme: TypeAlias = Literal["neutral", "technical", "warm", "mono"]
ArtifactKind: TypeAlias = Literal[
    "implementation_plan",
    "code_review_explainer",
    "design_variant_grid",
    "research_report",
    "custom_editor",
]


class ArtifactBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SummaryItem(ArtifactBaseModel):
    label: str = Field(max_length=80)
    value: str = Field(max_length=240)
    tone: Tone = "neutral"


class SummarySection(ArtifactBaseModel):
    kind: Literal["summary"]
    title: str | None = Field(default=None, max_length=120)
    items: list[SummaryItem] = Field(min_length=1, max_length=12)


class NarrativeSection(ArtifactBaseModel):
    kind: Literal["narrative"]
    title: str | None = Field(default=None, max_length=120)
    body: str = Field(max_length=MAX_BODY_LENGTH)


class CalloutSection(ArtifactBaseModel):
    kind: Literal["callout"]
    title: str | None = Field(default=None, max_length=120)
    body: str = Field(max_length=4_000)
    tone: Tone = "neutral"


class ChecklistItem(ArtifactBaseModel):
    text: str = Field(max_length=300)
    checked: bool = False
    priority: Literal["low", "medium", "high"] = "medium"


class ChecklistSection(ArtifactBaseModel):
    kind: Literal["checklist"]
    title: str = Field(max_length=120)
    items: list[ChecklistItem] = Field(min_length=1, max_length=50)


class TableColumn(ArtifactBaseModel):
    key: str = Field(pattern=r"^[a-zA-Z_][a-zA-Z0-9_\-]*$", max_length=64)
    label: str = Field(max_length=80)


TableValue: TypeAlias = str | int | float | bool | None


class TableSection(ArtifactBaseModel):
    kind: Literal["table"]
    title: str = Field(max_length=120)
    columns: list[TableColumn] = Field(min_length=1, max_length=MAX_COLUMNS)
    rows: list[dict[str, TableValue]] = Field(default_factory=list, max_length=MAX_ROWS)


class ComparisonOption(ArtifactBaseModel):
    id: str = Field(max_length=64)
    label: str = Field(max_length=120)
    summary: str | None = Field(default=None, max_length=400)
    attributes: dict[str, str] = Field(default_factory=dict)
    recommendation: Literal["yes", "no", "maybe"] | None = None


class ComparisonSection(ArtifactBaseModel):
    kind: Literal["comparison"]
    title: str = Field(max_length=120)
    options: list[ComparisonOption] = Field(min_length=2, max_length=8)


class MatrixCell(ArtifactBaseModel):
    x: str = Field(max_length=80)
    y: str = Field(max_length=80)
    label: str = Field(max_length=240)
    tone: Tone = "neutral"


class MatrixSection(ArtifactBaseModel):
    kind: Literal["matrix"]
    title: str = Field(max_length=120)
    x_axis: str = Field(max_length=80)
    y_axis: str = Field(max_length=80)
    cells: list[MatrixCell] = Field(min_length=1, max_length=64)


class TimelineEvent(ArtifactBaseModel):
    label: str = Field(max_length=160)
    date: str | None = Field(default=None, max_length=80)
    body: str | None = Field(default=None, max_length=600)
    status: Literal["done", "active", "planned", "blocked"] = "planned"


class TimelineSection(ArtifactBaseModel):
    kind: Literal["timeline"]
    title: str = Field(max_length=120)
    events: list[TimelineEvent] = Field(min_length=1, max_length=30)


class FlowNode(ArtifactBaseModel):
    id: str = Field(max_length=64)
    label: str = Field(max_length=120)
    description: str | None = Field(default=None, max_length=300)


class FlowEdge(ArtifactBaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_: str = Field(alias="from", max_length=64)
    to: str = Field(max_length=64)
    label: str | None = Field(default=None, max_length=120)


class FlowSection(ArtifactBaseModel):
    kind: Literal["flow"]
    title: str = Field(max_length=120)
    nodes: list[FlowNode] = Field(min_length=1, max_length=24)
    edges: list[FlowEdge] = Field(default_factory=list, max_length=48)


class CodeAnnotation(ArtifactBaseModel):
    line: int = Field(ge=1)
    severity: Literal["info", "warning", "danger"] = "info"
    comment: str = Field(max_length=600)


class CodeSection(ArtifactBaseModel):
    kind: Literal["code"]
    title: str = Field(max_length=120)
    language: str | None = Field(default=None, max_length=40)
    code: str = Field(max_length=MAX_CODE_LENGTH)
    annotations: list[CodeAnnotation] = Field(default_factory=list, max_length=50)


class DiffLine(ArtifactBaseModel):
    type: Literal["context", "add", "remove"]
    old_line: int | None = Field(default=None, ge=1)
    new_line: int | None = Field(default=None, ge=1)
    text: str = Field(max_length=1_000)


class DiffHunk(ArtifactBaseModel):
    header: str | None = Field(default=None, max_length=160)
    lines: list[DiffLine] = Field(min_length=1, max_length=300)


class DiffAnnotation(ArtifactBaseModel):
    line: int | None = Field(default=None, ge=1)
    severity: Literal["info", "warning", "danger"]
    comment: str = Field(max_length=600)


class DiffFile(ArtifactBaseModel):
    path: str = Field(max_length=260)
    hunks: list[DiffHunk] = Field(min_length=1, max_length=20)
    annotations: list[DiffAnnotation] = Field(default_factory=list, max_length=50)


class DiffReviewSection(ArtifactBaseModel):
    kind: Literal["diff_review"]
    title: str = Field(max_length=120)
    files: list[DiffFile] = Field(min_length=1, max_length=20)


class Variant(ArtifactBaseModel):
    id: str = Field(max_length=64)
    name: str = Field(max_length=120)
    description: str = Field(max_length=600)
    strengths: list[str] = Field(default_factory=list, max_length=8)
    weaknesses: list[str] = Field(default_factory=list, max_length=8)
    selected: bool = False
    html_preview: str | None = Field(default=None, max_length=4_000)


class VariantGridSection(ArtifactBaseModel):
    kind: Literal["variant_grid"]
    title: str = Field(max_length=120)
    variants: list[Variant] = Field(min_length=1, max_length=8)


class EditableColumn(ArtifactBaseModel):
    key: str = Field(pattern=r"^[a-zA-Z_][a-zA-Z0-9_\-]*$", max_length=64)
    label: str = Field(max_length=80)
    input: Literal["text", "number", "select", "checkbox"]
    options: list[str] = Field(default_factory=list, max_length=20)


class EditableTableSection(ArtifactBaseModel):
    kind: Literal["editable_table"]
    title: str = Field(max_length=120)
    columns: list[EditableColumn] = Field(min_length=1, max_length=MAX_COLUMNS)
    rows: list[dict[str, TableValue]] = Field(default_factory=list, max_length=MAX_ROWS)


class BoardCard(ArtifactBaseModel):
    id: str = Field(max_length=64)
    title: str = Field(max_length=160)
    body: str | None = Field(default=None, max_length=800)
    tone: Tone = "neutral"


class BoardColumn(ArtifactBaseModel):
    id: str = Field(max_length=64)
    title: str = Field(max_length=120)
    cards: list[BoardCard] = Field(default_factory=list, max_length=30)


class BoardSection(ArtifactBaseModel):
    kind: Literal["board"]
    title: str = Field(max_length=120)
    columns: list[BoardColumn] = Field(min_length=1, max_length=8)


class ArtifactSource(ArtifactBaseModel):
    id: str | None = Field(default=None, max_length=64)
    title: str = Field(max_length=200)
    url: str | None = Field(default=None, max_length=1_000)
    note: str | None = Field(default=None, max_length=500)


class SourceListSection(ArtifactBaseModel):
    kind: Literal["source_list"]
    title: str | None = Field(default=None, max_length=120)
    sources: list[ArtifactSource] = Field(default_factory=list, max_length=MAX_SOURCES)


ArtifactSection: TypeAlias = Annotated[
    SummarySection
    | NarrativeSection
    | CalloutSection
    | ChecklistSection
    | TableSection
    | ComparisonSection
    | MatrixSection
    | TimelineSection
    | FlowSection
    | CodeSection
    | DiffReviewSection
    | VariantGridSection
    | EditableTableSection
    | BoardSection
    | SourceListSection,
    Field(discriminator="kind"),
]


class CopyAsJsonAction(ArtifactBaseModel):
    kind: Literal["copy_as_json"]
    label: str = Field(max_length=120)
    data_path: str | None = Field(default=None, max_length=200)


class CopyAsMarkdownAction(ArtifactBaseModel):
    kind: Literal["copy_as_markdown"]
    label: str = Field(max_length=120)
    template: str | None = Field(default=None, max_length=4_000)


class CopyAsPromptAction(ArtifactBaseModel):
    kind: Literal["copy_as_prompt"]
    label: str = Field(max_length=120)
    payload: str = Field(max_length=MAX_BODY_LENGTH)


class EmitIntentAction(ArtifactBaseModel):
    kind: Literal["emit_intent"]
    label: str = Field(max_length=120)
    intent: str = Field(max_length=120)
    payload: dict[str, Any] | None = None


ArtifactAction: TypeAlias = Annotated[
    CopyAsJsonAction | CopyAsMarkdownAction | CopyAsPromptAction | EmitIntentAction,
    Field(discriminator="kind"),
]


class ArtifactSpec(ArtifactBaseModel):
    v: Literal["0.1"] = "0.1"
    artifact: ArtifactKind
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    subtitle: str | None = Field(default=None, max_length=240)
    audience: Audience = "team"
    density: Density = "normal"
    theme: Theme = "neutral"
    sections: list[ArtifactSection] = Field(min_length=1, max_length=MAX_SECTIONS)
    actions: list[ArtifactAction] = Field(default_factory=list, max_length=MAX_ACTIONS)
    sources: list[ArtifactSource] = Field(default_factory=list, max_length=MAX_SOURCES)
    metadata: dict[str, Any] = Field(default_factory=dict)
