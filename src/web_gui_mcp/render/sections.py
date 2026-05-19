from __future__ import annotations

import json
from typing import Any

from web_gui_mcp.render.runtime import render_sandbox_runtime_js
from web_gui_mcp.schema.artifact import (
    AnimationControlsSection,
    BoardSection,
    CalloutSection,
    ChartPanelSection,
    ChecklistSection,
    CodeSection,
    ComparisonSection,
    ComponentMatrixSection,
    CopyableAssetGridSection,
    DependencyToggleListSection,
    DiffReviewSection,
    EditableTableSection,
    FilterableCollectionSection,
    FlowSection,
    InspectorDiagramSection,
    LogTimelineSection,
    MatrixSection,
    NarrativeSection,
    PromptTunerSection,
    PrototypeFlowSection,
    SlideDeckSection,
    SourceListSection,
    SplitViewSection,
    SummarySection,
    TableSection,
    TabsSection,
    TimelineSection,
    TokenSheetSection,
    VariantGridSection,
)
from web_gui_mcp.schema.tool_io import RenderOptions
from web_gui_mcp.util.escape import attr, h, safe_href


def render_section(section: Any, options: RenderOptions) -> str:
    body = _render_section_body(section, options)
    return f'<section class="gui2-section gui2-section-{attr(section.kind)}" data-kind="{attr(section.kind)}">{body}</section>'


def _section_heading(title: str | None) -> str:
    return f"<h2>{h(title)}</h2>" if title else ""


def _render_section_body(section: Any, options: RenderOptions) -> str:
    if isinstance(section, SummarySection):
        return render_summary(section)
    if isinstance(section, NarrativeSection):
        return render_narrative(section)
    if isinstance(section, CalloutSection):
        return render_callout(section)
    if isinstance(section, ChecklistSection):
        return render_checklist(section)
    if isinstance(section, TableSection):
        return render_table(section)
    if isinstance(section, ComparisonSection):
        return render_comparison(section)
    if isinstance(section, MatrixSection):
        return render_matrix(section)
    if isinstance(section, TimelineSection):
        return render_timeline(section)
    if isinstance(section, FlowSection):
        return render_flow(section)
    if isinstance(section, CodeSection):
        return render_code(section)
    if isinstance(section, DiffReviewSection):
        return render_diff_review(section)
    if isinstance(section, VariantGridSection):
        return render_variant_grid(section, options)
    if isinstance(section, EditableTableSection):
        return render_editable_table(section)
    if isinstance(section, BoardSection):
        return render_board(section)
    if isinstance(section, SourceListSection):
        return render_source_list(section)
    if isinstance(section, SplitViewSection):
        return render_split_view(section)
    if isinstance(section, TabsSection):
        return render_tabs(section)
    if isinstance(section, FilterableCollectionSection):
        return render_filterable_collection(section)
    if isinstance(section, InspectorDiagramSection):
        return render_inspector_diagram(section)
    if isinstance(section, PrototypeFlowSection):
        return render_prototype_flow(section)
    if isinstance(section, AnimationControlsSection):
        return render_animation_controls(section)
    if isinstance(section, TokenSheetSection):
        return render_token_sheet(section)
    if isinstance(section, ComponentMatrixSection):
        return render_component_matrix(section)
    if isinstance(section, SlideDeckSection):
        return render_slide_deck(section)
    if isinstance(section, ChartPanelSection):
        return render_chart_panel(section)
    if isinstance(section, LogTimelineSection):
        return render_log_timeline(section)
    if isinstance(section, DependencyToggleListSection):
        return render_dependency_toggle_list(section)
    if isinstance(section, PromptTunerSection):
        return render_prompt_tuner(section)
    if isinstance(section, CopyableAssetGridSection):
        return render_copyable_asset_grid(section)
    raise TypeError(f"Unsupported section type: {type(section).__name__}")


def render_summary(section: SummarySection) -> str:
    cards = []
    for item in section.items:
        cards.append(
            f'<div class="gui2-card gui2-tone-{attr(item.tone)}">'
            f'<div class="gui2-label">{h(item.label)}</div>'
            f'<div class="gui2-value">{h(item.value)}</div>'
            "</div>"
        )
    return _section_heading(section.title) + f'<div class="gui2-grid gui2-summary-grid">{"".join(cards)}</div>'


def render_narrative(section: NarrativeSection) -> str:
    return _section_heading(section.title) + _paragraphs(section.body)


def render_callout(section: CalloutSection) -> str:
    return (
        f'<div class="gui2-callout gui2-tone-{attr(section.tone)}">'
        f"{_section_heading(section.title)}{_paragraphs(section.body)}"
        "</div>"
    )


def render_checklist(section: ChecklistSection) -> str:
    items = []
    for item in section.items:
        checked = " checked" if item.checked else ""
        items.append(
            "<li>"
            f'<input type="checkbox" disabled{checked} aria-label="{attr(item.text)}">'
            f"<span>{h(item.text)}</span>"
            f'<span class="gui2-priority">{h(item.priority)}</span>'
            "</li>"
        )
    return _section_heading(section.title) + f'<ul class="gui2-checklist">{"".join(items)}</ul>'


def render_table(section: TableSection) -> str:
    return _section_heading(section.title) + _table(section.columns, section.rows)


def render_comparison(section: ComparisonSection) -> str:
    cards = []
    for option in section.options:
        attrs = "".join(
            f'<li><span class="gui2-label">{h(key)}</span>: {h(value)}</li>'
            for key, value in option.attributes.items()
        )
        recommendation = (
            f'<span class="gui2-badge">{h(option.recommendation)}</span>'
            if option.recommendation
            else ""
        )
        cards.append(
            '<article class="gui2-card">'
            f"<h3>{h(option.label)} {recommendation}</h3>"
            f"{_paragraphs(option.summary or '')}"
            f'<ul class="gui2-list">{attrs}</ul>'
            "</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-comparison">{"".join(cards)}</div>'


def render_matrix(section: MatrixSection) -> str:
    cells = []
    for cell in section.cells:
        cells.append(
            f'<article class="gui2-card gui2-tone-{attr(cell.tone)}">'
            f'<div class="gui2-label">{h(section.x_axis)}: {h(cell.x)}</div>'
            f'<div class="gui2-label">{h(section.y_axis)}: {h(cell.y)}</div>'
            f'<div class="gui2-value">{h(cell.label)}</div>'
            "</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-grid gui2-summary-grid">{"".join(cells)}</div>'


def render_timeline(section: TimelineSection) -> str:
    items = []
    for event in section.events:
        date = event.date or event.status
        body = f'<p class="gui2-muted">{h(event.body)}</p>' if event.body else ""
        items.append(
            "<li>"
            f'<div class="gui2-status">{h(date)}</div>'
            f"<div><strong>{h(event.label)}</strong>{body}</div>"
            "</li>"
        )
    return _section_heading(section.title) + f'<ol class="gui2-timeline">{"".join(items)}</ol>'


def render_flow(section: FlowSection) -> str:
    nodes = []
    labels = {node.id: node.label for node in section.nodes}
    for node in section.nodes:
        nodes.append(
            '<article class="gui2-card">'
            f"<h3>{h(node.label)}</h3>{_paragraphs(node.description or '')}"
            "</article>"
        )
    edges = []
    for edge in section.edges:
        edge_label = f" ({h(edge.label)})" if edge.label else ""
        edges.append(f"<li>{h(labels.get(edge.from_, edge.from_))} -> {h(labels.get(edge.to, edge.to))}{edge_label}</li>")
    edge_html = f'<ul class="gui2-list">{"".join(edges)}</ul>' if edges else ""
    return _section_heading(section.title) + f'<div class="gui2-flow-nodes">{"".join(nodes)}</div>{edge_html}'


def render_code(section: CodeSection) -> str:
    lines = section.code.splitlines() or [""]
    rendered_lines = [
        f'<span class="gui2-code-line" data-line="{line_no}">{h(line)}</span>'
        for line_no, line in enumerate(lines, start=1)
    ]
    annotations = _render_annotations(
        [
            {"line": note.line, "severity": note.severity, "comment": note.comment}
            for note in section.annotations
        ]
    )
    language = f'<span class="gui2-badge">{h(section.language)}</span>' if section.language else ""
    return (
        _section_heading(section.title)
        + language
        + f'<pre class="gui2-code"><code>{"".join(rendered_lines)}</code></pre>'
        + annotations
    )


def render_diff_review(section: DiffReviewSection) -> str:
    files = []
    for file in section.files:
        hunks = []
        for hunk in file.hunks:
            header = f'<div class="gui2-label">{h(hunk.header)}</div>' if hunk.header else ""
            rows = []
            for line in hunk.lines:
                prefix = {"context": " ", "add": "+", "remove": "-"}[line.type]
                line_no = line.new_line if line.type == "add" else line.old_line
                rows.append(
                    f'<tr class="gui2-diff-line-{attr(line.type)}">'
                    f'<td class="gui2-diff-prefix">{h(prefix)}</td>'
                    f"<td>{h(line_no or '')}</td>"
                    f"<td><code>{h(line.text)}</code></td>"
                    "</tr>"
                )
            hunks.append(
                f'{header}<div class="gui2-table-wrap"><table><tbody>{"".join(rows)}</tbody></table></div>'
            )
        annotations = _render_annotations(
            [
                {"line": note.line, "severity": note.severity, "comment": note.comment}
                for note in file.annotations
            ]
        )
        files.append(
            '<article class="gui2-card">'
            f"<h3>{h(file.path)}</h3>{''.join(hunks)}{annotations}"
            "</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-grid">{"".join(files)}</div>'


def render_variant_grid(section: VariantGridSection, options: RenderOptions) -> str:
    cards = []
    for variant in section.variants:
        marker = '<span class="gui2-badge">selected</span>' if variant.selected else ""
        strengths = "".join(f"<li>{h(item)}</li>" for item in variant.strengths)
        weaknesses = "".join(f"<li>{h(item)}</li>" for item in variant.weaknesses)
        preview = ""
        if variant.html_preview:
            if options.allow_trusted_html_preview:
                preview = f'<div class="gui2-preview">{variant.html_preview}</div>'
            else:
                preview = f'<pre class="gui2-preview">{h(variant.html_preview)}</pre>'
        cards.append(
            '<article class="gui2-card">'
            f"<h3>{h(variant.name)} {marker}</h3>"
            f"{_paragraphs(variant.description)}"
            f'<div class="gui2-label">Strengths</div><ul class="gui2-list">{strengths}</ul>'
            f'<div class="gui2-label">Weaknesses</div><ul class="gui2-list">{weaknesses}</ul>'
            f"{preview}</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-variants">{"".join(cards)}</div>'


def render_editable_table(section: EditableTableSection) -> str:
    header = "".join(f"<th>{h(column.label)}</th>" for column in section.columns)
    rows = []
    for row in section.rows:
        cells = []
        for column in section.columns:
            value = row.get(column.key)
            if column.input == "select":
                options = "".join(
                    f'<option value="{attr(option)}"{" selected" if option == value else ""}>{h(option)}</option>'
                    for option in column.options
                )
                control = f'<select class="gui2-form-input" data-key="{attr(column.key)}">{options}</select>'
            elif column.input == "checkbox":
                control = (
                    f'<input class="gui2-form-input" type="checkbox" data-key="{attr(column.key)}"'
                    f'{" checked" if bool(value) else ""}>'
                )
            else:
                input_type = "number" if column.input == "number" else "text"
                control = (
                    f'<input class="gui2-form-input" type="{input_type}" data-key="{attr(column.key)}"'
                    f' value="{attr(value if value is not None else "")}">'
                )
            cells.append(f"<td>{control}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return (
        _section_heading(section.title)
        + f'<div class="gui2-table-wrap"><table><thead><tr>{header}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    )


def render_board(section: BoardSection) -> str:
    columns = []
    for column in section.columns:
        cards = []
        for card in column.cards:
            body = _paragraphs(card.body or "")
            cards.append(
                f'<article class="gui2-card gui2-tone-{attr(card.tone)}" draggable="true" data-gui2-drag-card data-gui2-card-id="{attr(card.id)}">'
                f"<h3>{h(card.title)}</h3>{body}"
                "</article>"
            )
        columns.append(
            f'<section class="gui2-board-column" data-gui2-drop-zone data-gui2-column-id="{attr(column.id)}">'
            f"<h3>{h(column.title)}</h3>{''.join(cards)}"
            "</section>"
        )
    return _section_heading(section.title) + f'<div class="gui2-board">{"".join(columns)}</div>'


def render_source_list(section: SourceListSection) -> str:
    items = []
    for source in section.sources:
        href = safe_href(source.url)
        title = f'<a href="{attr(href)}" rel="noreferrer">{h(source.title)}</a>' if href else h(source.title)
        note = f'<div class="gui2-muted">{h(source.note)}</div>' if source.note else ""
        items.append(f"<li>{title}{note}</li>")
    return _section_heading(section.title or "Sources") + f'<ol class="gui2-sources">{"".join(items)}</ol>'


def render_split_view(section: SplitViewSection) -> str:
    return (
        _section_heading(section.title)
        + f'<div class="gui2-split gui2-split-{attr(section.ratio)}">'
        + '<article class="gui2-sheet-panel">'
        + f"<h3>{h(section.left_title)}</h3>{_paragraphs(section.left_body)}</article>"
        + '<article class="gui2-sheet-panel accent">'
        + f"<h3>{h(section.right_title)}</h3>{_paragraphs(section.right_body)}</article>"
        + "</div>"
    )


def render_tabs(section: TabsSection) -> str:
    active = next((tab.id for tab in section.tabs if tab.active), section.tabs[0].id)
    controls = []
    panels = []
    for tab in section.tabs:
        badge = f'<span class="gui2-tab-badge">{h(tab.badge)}</span>' if tab.badge else ""
        selected = "true" if tab.id == active else "false"
        controls.append(
            f'<button class="gui2-tab" type="button" data-gui2-tab="{attr(tab.id)}" aria-selected="{selected}">{h(tab.label)}{badge}</button>'
        )
        panels.append(
            f'<article class="gui2-tab-panel" data-gui2-panel="{attr(tab.id)}">'
            f"<h3>{h(tab.label)}</h3>{_paragraphs(tab.body)}</article>"
        )
    return (
        _section_heading(section.title)
        + '<div class="gui2-tabs" data-gui2-tabs>'
        + f'<div class="gui2-tablist" role="tablist">{"".join(controls)}</div>'
        + f'<div class="gui2-tab-panels">{"".join(panels)}</div>'
        + "</div>"
    )


def render_filterable_collection(section: FilterableCollectionSection) -> str:
    items = []
    for item in section.items:
        tag_html = "".join(f'<span class="gui2-badge">{h(tag)}</span>' for tag in item.tags)
        filter_text = " ".join([item.title, item.body, *item.tags]).casefold()
        items.append(
            f'<article class="gui2-card gui2-tone-{attr(item.tone)}" data-gui2-filter-item data-gui2-filter-text="{attr(filter_text)}">'
            f"<h3>{h(item.title)}</h3>{_paragraphs(item.body)}"
            f'<div class="gui2-chip-row">{tag_html}</div></article>'
        )
    return (
        _section_heading(section.title)
        + '<div class="gui2-filterable" data-gui2-filter-root>'
        + f'<label class="gui2-filter-label"><span>Filter</span><input class="gui2-form-input" data-gui2-filter placeholder="{attr(section.placeholder)}"></label>'
        + f'<div class="gui2-card-grid">{"".join(items)}</div>'
        + "</div>"
    )


def render_inspector_diagram(section: InspectorDiagramSection) -> str:
    nodes = []
    for node in section.nodes:
        nodes.append(
            f'<button class="gui2-diagram-node gui2-tone-{attr(node.tone)}" type="button" data-gui2-inspect data-gui2-title="{attr(node.label)}" data-gui2-body="{attr(node.description)}" style="left:{node.x}%;top:{node.y}%;">'
            f"{h(node.label)}</button>"
        )
    positions = {node.id: node for node in section.nodes}
    edge_lines = []
    for edge in section.edges:
        start = positions.get(edge.from_)
        end = positions.get(edge.to)
        if start and end:
            edge_lines.append(
                f'<line x1="{start.x}" y1="{start.y}" x2="{end.x}" y2="{end.y}"></line>'
            )
    edge_svg = (
        '<svg class="gui2-diagram-edges" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'
        + "".join(edge_lines)
        + "</svg>"
    )
    edges = "".join(
        f'<li>{h(edge.from_)} -> {h(edge.to)}{": " + h(edge.label) if edge.label else ""}</li>'
        for edge in section.edges
    )
    return (
        _section_heading(section.title)
        + '<div class="gui2-diagram-layout" data-gui2-diagram>'
        + f'<div class="gui2-diagram-canvas">{edge_svg}{"".join(nodes)}</div>'
        + '<aside class="gui2-inspector"><div class="gui2-label">Inspector</div>'
        + '<h3 data-gui2-inspector-title></h3><p data-gui2-inspector-body class="gui2-muted"></p>'
        + f'<ul class="gui2-list">{edges}</ul></aside></div>'
    )


def render_prototype_flow(section: PrototypeFlowSection) -> str:
    screens = []
    for screen in section.screens:
        links = [
            link for link in section.links if link.from_ == screen.id
        ]
        buttons = "".join(
            f'<button type="button" data-prototype-target="{attr(link.to)}">{h(link.label)}</button>'
            for link in links
        )
        cta = f'<div class="sandbox-cta">{h(screen.cta)}</div>' if screen.cta else ""
        screens.append(
            f'<article class="sandbox-screen" data-screen="{attr(screen.id)}">'
            f"<h2>{h(screen.title)}</h2>{_paragraphs(screen.body)}{cta}<div class=\"sandbox-actions\">{buttons}</div></article>"
        )
    return _section_heading(section.title) + _sandbox_iframe(section.title, "".join(screens))


def render_animation_controls(section: AnimationControlsSection) -> str:
    presets = []
    first = section.presets[0]
    for preset in section.presets:
        presets.append(
            '<article class="sandbox-card">'
            f"<h3>{h(preset.label)}</h3>{_paragraphs(preset.description or '')}"
            f'<button type="button" data-animation-replay style="--duration:{preset.duration_ms}ms;--easing:{attr(preset.easing)}">Replay</button>'
            "</article>"
        )
    body = (
        f'<div class="sandbox-stage"><div class="sandbox-puck run">{h(section.preview_label)}</div></div>'
        f'<label class="sandbox-field">Duration <input type="range" min="50" max="5000" value="{first.duration_ms}" data-duration></label>'
        '<div class="sandbox-actions"><button type="button" data-step-duration="-50">-50ms</button><button type="button" data-step-duration="50">+50ms</button></div>'
        + "".join(presets)
    )
    return _section_heading(section.title) + _sandbox_iframe(section.title, body)


def render_token_sheet(section: TokenSheetSection) -> str:
    groups = []
    for group in section.groups:
        tokens = []
        for token in group.tokens:
            tokens.append(
                '<article class="gui2-token">'
                f'<div class="gui2-token-swatch" data-token-value="{attr(token.value)}"></div>'
                f"<h3>{h(token.name)}</h3><code>{h(token.value)}</code>"
                f"{_paragraphs(token.description or '')}"
                f'<button class="gui2-button secondary" data-gui2-action="copy-payload" data-gui2-payload="{attr(json.dumps(token.value))}">Copy</button>'
                "</article>"
            )
        groups.append(f'<section class="gui2-token-group"><h3>{h(group.title)}</h3><div class="gui2-card-grid">{"".join(tokens)}</div></section>')
    return _section_heading(section.title) + "".join(groups)


def render_component_matrix(section: ComponentMatrixSection) -> str:
    cards = []
    for variant in section.variants:
        selected = '<span class="gui2-badge">selected</span>' if variant.selected else ""
        cards.append(
            '<article class="gui2-card gui2-variant-cell">'
            f"<h3>{h(variant.name)} {selected}</h3>"
            '<div class="gui2-component-preview">'
            f'<div class="gui2-component-specimen" data-state="{attr(variant.state)}" data-intent="{attr(variant.intent)}">'
            f"{h(section.component)}</div></div>"
            f'<div class="gui2-label">{h(section.component)} / {h(variant.intent)} / {h(variant.state)}</div>'
            f"{_paragraphs(variant.notes or '')}</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-component-matrix">{"".join(cards)}</div>'


def render_slide_deck(section: SlideDeckSection) -> str:
    slides = []
    for slide in section.slides:
        kicker = f'<div class="gui2-kicker">{h(slide.kicker)}</div>' if slide.kicker else ""
        notes = f'<aside class="gui2-slide-notes">{_paragraphs(slide.notes)}</aside>' if slide.notes else ""
        slides.append(
            f'<article class="gui2-slide" data-gui2-slide data-slide-id="{attr(slide.id)}">'
            f"{kicker}<h3>{h(slide.title)}</h3>{_paragraphs(slide.body)}{notes}</article>"
        )
    return (
        _section_heading(section.title)
        + '<div class="gui2-slide-deck" data-gui2-slide-deck tabindex="0">'
        + '<div class="gui2-slide-toolbar">'
        + '<button type="button" class="gui2-button secondary" data-gui2-slide-control="prev">Prev</button>'
        + '<span data-gui2-slide-count></span>'
        + '<button type="button" class="gui2-button secondary" data-gui2-slide-control="next">Next</button>'
        + f'</div>{"".join(slides)}</div>'
    )


def render_chart_panel(section: ChartPanelSection) -> str:
    max_value = max((datum.value for datum in section.data), default=1) or 1
    rows = []
    for datum in section.data:
        width = max(1, min(100, int((datum.value / max_value) * 100)))
        rows.append(
            f'<div class="gui2-chart-row gui2-tone-{attr(datum.tone)}">'
            f'<span>{h(datum.label)}</span><div class="gui2-chart-track"><i style="width:{width}%"></i></div><strong>{h(datum.value)}</strong></div>'
        )
    return _section_heading(section.title) + f'<div class="gui2-chart-panel" data-chart-type="{attr(section.chart_type)}">{"".join(rows)}</div>'


def render_log_timeline(section: LogTimelineSection) -> str:
    events = []
    for event in section.events:
        detail = (
            f"<details><summary>Details</summary><pre>{h(event.detail)}</pre></details>"
            if event.detail
            else ""
        )
        events.append(
            f'<li class="gui2-log-event gui2-log-{attr(event.level)}">'
            f'<time>{h(event.timestamp)}</time><strong>{h(event.level)}</strong><span>{h(event.message)}</span>{detail}</li>'
        )
    return _section_heading(section.title) + f'<ol class="gui2-log-timeline">{"".join(events)}</ol>'


def render_dependency_toggle_list(section: DependencyToggleListSection) -> str:
    rows = []
    for toggle in section.toggles:
        deps = ",".join(toggle.depends_on)
        checked = " checked" if toggle.enabled else ""
        warning = f'<div class="sandbox-warning">{h(toggle.warning or "Dependency is disabled.")}</div>'
        rows.append(
            f'<label class="sandbox-toggle" data-toggle-row data-toggle-id="{attr(toggle.id)}" data-depends="{attr(deps)}">'
            f'<input type="checkbox"{checked}>'
            f'<span><strong>{h(toggle.label)}</strong>{_paragraphs(toggle.description or "")}{warning}</span></label>'
        )
    body = "".join(rows) + '<button type="button" data-copy="Feature flag diff">Copy diff</button>'
    return _section_heading(section.title) + _sandbox_iframe(section.title, body)


def render_prompt_tuner(section: PromptTunerSection) -> str:
    variables = "".join(
        f'<label class="sandbox-field">{h(variable.label)}<input data-prompt-var="{attr(variable.name)}" value="{attr(variable.value)}"></label>'
        for variable in section.variables
    )
    samples = "".join(
        f'<article class="sandbox-card"><h3>{h(sample.label)}</h3>{_paragraphs(sample.input)}{_paragraphs(sample.expected or "")}</article>'
        for sample in section.samples
    )
    body = (
        f'<textarea data-prompt-template>{h(section.template)}</textarea>'
        f'<div class="sandbox-grid">{variables}</div>'
        '<pre data-prompt-preview></pre>'
        f'<div class="sandbox-grid">{samples}</div>'
        f'<button type="button" data-copy="{attr(section.template)}">Copy template</button>'
    )
    return _section_heading(section.title) + _sandbox_iframe(section.title, body)


def render_copyable_asset_grid(section: CopyableAssetGridSection) -> str:
    assets = []
    for asset in section.assets:
        payload = json.dumps(asset.content, ensure_ascii=False)
        assets.append(
            '<article class="gui2-card">'
            f'<div class="gui2-label">{h(asset.kind)}</div><h3>{h(asset.title)}</h3>'
            f"{_paragraphs(asset.description or '')}<pre class=\"gui2-preview\">{h(asset.content)}</pre>"
            f'<button class="gui2-button secondary" data-gui2-action="copy-payload" data-gui2-payload="{attr(payload)}">Copy asset</button>'
            "</article>"
        )
    return _section_heading(section.title) + f'<div class="gui2-card-grid">{"".join(assets)}</div>'


def _sandbox_iframe(title: str, body: str) -> str:
    srcdoc = _sandbox_doc(title, body)
    return (
        '<div class="gui2-sandbox-shell">'
        f'<iframe title="{attr(title)}" sandbox="allow-scripts" loading="lazy" referrerpolicy="no-referrer" srcdoc="{attr(srcdoc)}"></iframe>'
        "</div>"
    )


def _sandbox_doc(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'">
<title>{h(title)}</title>
<style>{_sandbox_css()}</style>
</head>
<body>
<main class="sandbox-shell">
{body}
</main>
<script>{render_sandbox_runtime_js()}</script>
</body>
</html>"""


def _sandbox_css() -> str:
    return """
:root { --ink:#1d1d1f; --paper:#f5f5f7; --line:#d2d2d7; --accent:#0071e3; --blue:#0066cc; --duration:260ms; --shadow:0 14px 32px rgba(0,0,0,.08); }
* { box-sizing:border-box; }
[hidden] { display:none !important; }
body { margin:0; background:var(--paper); color:var(--ink); font:15px/1.6 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif; }
p { margin:0; max-width:64ch; line-height:1.66; }
p + p { margin-top:10px; }
h2, h3 { margin:0; line-height:1.15; }
button, input, textarea { font:inherit; }
button { border:1px solid var(--accent); background:var(--accent); color:white; border-radius:999px; padding:8px 14px; cursor:pointer; }
button:hover { background:#147ce5; border-color:#147ce5; }
input, textarea { width:100%; border:1px solid var(--line); border-radius:8px; padding:10px 12px; background:#fff; color:var(--ink); }
textarea { min-height:140px; }
.sandbox-shell { display:grid; gap:14px; padding:18px; min-height:320px; }
.sandbox-screen, .sandbox-card, .sandbox-toggle { display:grid; gap:11px; align-content:start; border:1px solid var(--line); border-radius:8px; background:#fff; padding:16px; margin:0; box-shadow:var(--shadow); }
.sandbox-actions, .sandbox-grid { display:flex; flex-wrap:wrap; gap:10px; }
.sandbox-actions { position:sticky; bottom:0; padding-top:8px; background:linear-gradient(transparent, var(--paper) 34%); }
.sandbox-grid { align-items:start; }
.sandbox-stage { height:150px; border:1px dashed var(--line); border-radius:8px; display:grid; align-items:center; padding:16px; background:#fff; }
.sandbox-puck { width:130px; padding:18px; background:var(--blue); color:white; border-radius:8px; text-align:center; transform:translateX(0); }
.sandbox-puck.run { animation:slide var(--duration) cubic-bezier(.2,.8,.2,1) both; }
@keyframes slide { to { transform:translateX(calc(100vw - 190px)); } }
.sandbox-field { display:grid; gap:6px; min-width:180px; margin:8px 0; }
.sandbox-toggle { display:flex; gap:12px; align-items:flex-start; box-shadow:none; }
.sandbox-toggle input { width:auto; margin-top:4px; accent-color:var(--accent); }
.sandbox-toggle[data-blocked="true"] { border-color:var(--accent); }
.sandbox-warning { display:none; color:var(--accent); font-weight:700; }
.sandbox-toggle[data-blocked="true"] .sandbox-warning { display:block; }
pre { white-space:pre-wrap; background:#1d1d1f; color:#f5f5f7; border-radius:8px; padding:12px; overflow:auto; }
""".strip()


def render_actions(actions: list[Any], options: RenderOptions) -> str:
    if not actions:
        return ""
    buttons = []
    for action in actions:
        if action.kind == "copy_as_json":
            buttons.append(
                f'<button class="gui2-button" data-gui2-action="copy-json">{h(action.label)}</button>'
            )
        elif action.kind == "copy_as_markdown":
            payload = json.dumps(action.template or "", ensure_ascii=False)
            buttons.append(
                f'<button class="gui2-button" data-gui2-action="copy-markdown" data-gui2-payload="{attr(payload)}">{h(action.label)}</button>'
            )
        elif action.kind == "copy_as_prompt":
            payload = json.dumps(action.payload, ensure_ascii=False)
            buttons.append(
                f'<button class="gui2-button" data-gui2-action="copy-prompt" data-gui2-payload="{attr(payload)}">{h(action.label)}</button>'
            )
        elif action.kind == "emit_intent":
            payload = json.dumps(
                {"intent": action.intent, "payload": action.payload or {}},
                ensure_ascii=False,
                sort_keys=True,
            )
            buttons.append(
                f'<button class="gui2-button secondary" data-gui2-action="emit-intent" data-gui2-payload="{attr(payload)}">{h(action.label)}</button>'
            )
    disabled_note = (
        '<span class="gui2-muted">Actions need local interactivity.</span>'
        if options.interactivity == "none"
        else ""
    )
    return f'<nav class="gui2-actions" aria-label="Artifact actions">{"".join(buttons)}{disabled_note}</nav>'


def _table(columns: Any, rows: list[dict[str, Any]]) -> str:
    header = "".join(f"<th>{h(column.label)}</th>" for column in columns)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{h(row.get(column.key, ''))}</td>" for column in columns)
        body_rows.append(f"<tr>{cells}</tr>")
    if not body_rows:
        body_rows.append(f'<tr><td colspan="{len(columns)}" class="gui2-muted">No rows</td></tr>')
    return f'<div class="gui2-table-wrap"><table><thead><tr>{header}</tr></thead><tbody>{"".join(body_rows)}</tbody></table></div>'


def _paragraphs(text: str) -> str:
    if not text:
        return ""
    paragraphs = []
    for part in text.split("\n\n"):
        lines = [h(line) for line in part.splitlines()]
        paragraphs.append(f"<p>{'<br>'.join(lines)}</p>")
    return "".join(paragraphs)


def _render_annotations(notes: list[dict[str, Any]]) -> str:
    if not notes:
        return ""
    items = []
    for note in notes:
        prefix = f"Line {note['line']}: " if note.get("line") else ""
        items.append(
            f'<li class="gui2-tone-{attr(note["severity"])}">{h(prefix)}{h(note["comment"])}</li>'
        )
    return f'<ul class="gui2-list">{"".join(items)}</ul>'
