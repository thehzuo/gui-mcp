from __future__ import annotations

from typing import Any

from gui2_artifact_mcp.schema.artifact import ArtifactSpec


def export_markdown(spec: ArtifactSpec) -> str:
    lines = [f"# {spec.title}", ""]
    if spec.subtitle:
        lines.extend([spec.subtitle, ""])
    for section in spec.sections:
        title = getattr(section, "title", None) or section.kind.replace("_", " ").title()
        lines.extend([f"## {title}", ""])
        lines.extend(_section_lines(section))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _section_lines(section: Any) -> list[str]:
    kind = section.kind
    if kind == "summary":
        return [f"- **{item.label}:** {item.value}" for item in section.items]
    if kind in {"narrative", "callout"}:
        return [section.body]
    if kind == "checklist":
        return [f"- [{'x' if item.checked else ' '}] {item.text}" for item in section.items]
    if kind in {"table", "editable_table"}:
        header = "| " + " | ".join(column.label for column in section.columns) + " |"
        divider = "| " + " | ".join("---" for _ in section.columns) + " |"
        rows = [
            "| " + " | ".join(str(row.get(column.key, "")) for column in section.columns) + " |"
            for row in section.rows
        ]
        return [header, divider, *rows]
    if kind == "comparison":
        return [f"- **{option.label}:** {option.summary or ''}" for option in section.options]
    if kind == "matrix":
        return [f"- {cell.x} / {cell.y}: {cell.label}" for cell in section.cells]
    if kind == "timeline":
        return [f"- {event.date or event.status}: {event.label}" for event in section.events]
    if kind == "flow":
        node_lines = [f"- {node.id}: {node.label}" for node in section.nodes]
        edge_lines = [f"- {edge.from_} -> {edge.to}" for edge in section.edges]
        return node_lines + edge_lines
    if kind == "code":
        language = section.language or ""
        return [f"```{language}", section.code, "```"]
    if kind == "diff_review":
        return [f"- {file.path}" for file in section.files]
    if kind == "variant_grid":
        return [f"- **{variant.name}:** {variant.description}" for variant in section.variants]
    if kind == "board":
        lines = []
        for column in section.columns:
            lines.append(f"### {column.title}")
            lines.extend(f"- {card.title}" for card in column.cards)
        return lines
    if kind == "source_list":
        return [f"- {source.title}: {source.url or ''}" for source in section.sources]
    return []
