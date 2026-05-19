from __future__ import annotations

from gui2_artifact_mcp.schema.artifact import Density, Theme


def render_css(theme: Theme = "neutral", density: Density = "normal") -> str:
    density_scale = {
        "compact": ("12px", "14px", "6px"),
        "normal": ("16px", "16px", "8px"),
        "presentation": ("22px", "18px", "8px"),
    }[density]
    theme_tokens = {
        "neutral": ("#fbf7ed", "#fffdf6", "#171512", "#6c6255"),
        "technical": ("#f6f7f2", "#fffefa", "#171512", "#5d655f"),
        "warm": ("#fbf4e7", "#fffaf0", "#201a14", "#76604e"),
        "mono": ("#f6f4ee", "#ffffff", "#12110f", "#66615a"),
    }[theme]
    gap, font_size, radius = density_scale
    bg, surface, text, muted = theme_tokens
    return f"""
:root {{
  --gui2-bg: {bg};
  --gui2-surface: {surface};
  --gui2-elevated: #ffffff;
  --gui2-border: #27231d;
  --gui2-text: {text};
  --gui2-muted: {muted};
  --gui2-good: #29724a;
  --gui2-warning: #9a6a12;
  --gui2-danger: #b53125;
  --gui2-info: #2458a6;
  --gui2-accent: #c43d2b;
  --gui2-blueprint: #2458a6;
  --gui2-gold: #c28c2d;
  --gui2-radius: {radius};
  --gui2-gap: {gap};
  --gui2-font-size: {font_size};
  --gui2-code-bg: #111827;
  --gui2-code-text: #f9fafb;
}}
* {{ box-sizing: border-box; }}
html {{ background: var(--gui2-bg); color: var(--gui2-text); }}
body {{
  margin: 0;
  font: 400 var(--gui2-font-size)/1.5 "Avenir Next", "Gill Sans", "Trebuchet MS", sans-serif;
  letter-spacing: 0;
  background:
    linear-gradient(rgba(39,35,29,.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(39,35,29,.045) 1px, transparent 1px),
    var(--gui2-bg);
  background-size: 28px 28px, 28px 28px, auto;
}}
a {{ color: var(--gui2-info); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
.gui2-shell {{
  container-type: inline-size;
  max-width: 1180px; margin: 0 auto; padding: clamp(16px, 4vw, 48px);
}}
.gui2-header {{ margin-bottom: calc(var(--gui2-gap) * 1.5); }}
.gui2-kicker {{
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px;
  color: var(--gui2-muted); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em;
}}
.gui2-header h1 {{
  margin: 0; max-width: 14ch;
  font: 500 clamp(2.3rem, 6vw, 5.2rem)/0.95 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  letter-spacing: 0;
}}
.gui2-subtitle {{ margin: 12px 0 0; max-width: 72ch; color: var(--gui2-muted); font-size: 1.05rem; }}
.gui2-section {{
  padding: calc(var(--gui2-gap) * 1.15) 0;
  border-top: 1.5px solid var(--gui2-border);
}}
.gui2-section h2 {{
  margin: 0 0 12px;
  font: 600 1.25rem/1.15 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  letter-spacing: 0;
}}
.gui2-section h3 {{ margin: 0 0 8px; font-size: 1rem; line-height: 1.25; letter-spacing: 0; }}
.gui2-grid {{ display: grid; gap: var(--gui2-gap); }}
.gui2-summary-grid {{ grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
.gui2-card, .gui2-callout, .gui2-board-column {{
  background: var(--gui2-surface);
  border: 1.5px solid var(--gui2-border);
  border-radius: var(--gui2-radius);
  padding: var(--gui2-gap);
  box-shadow: 6px 6px 0 rgba(39,35,29,.09);
}}
.gui2-label {{ color: var(--gui2-muted); font-size: 0.82rem; margin-bottom: 4px; }}
.gui2-value {{ font-weight: 650; }}
.gui2-tone-good {{ border-color: color-mix(in srgb, var(--gui2-good), var(--gui2-border) 65%); }}
.gui2-tone-warning {{ border-color: color-mix(in srgb, var(--gui2-warning), var(--gui2-border) 65%); }}
.gui2-tone-danger {{ border-color: color-mix(in srgb, var(--gui2-danger), var(--gui2-border) 65%); }}
.gui2-tone-info {{ border-color: color-mix(in srgb, var(--gui2-info), var(--gui2-border) 65%); }}
.gui2-badge {{
  display: inline-flex; align-items: center; min-height: 24px; padding: 2px 8px;
  border: 1px solid var(--gui2-border); border-radius: 999px; background: var(--gui2-surface);
  color: var(--gui2-muted); font-size: 0.78rem;
}}
.gui2-table-wrap {{ overflow-x: auto; border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); }}
table {{ width: 100%; border-collapse: collapse; min-width: 520px; background: var(--gui2-elevated); }}
th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--gui2-border); text-align: left; vertical-align: top; }}
th {{ background: var(--gui2-surface); font-size: 0.84rem; color: var(--gui2-muted); }}
tr:last-child td {{ border-bottom: 0; }}
.gui2-list {{ margin: 0; padding-left: 1.2rem; }}
.gui2-list li + li {{ margin-top: 8px; }}
.gui2-checklist {{ list-style: none; padding-left: 0; }}
.gui2-checklist li {{ display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; }}
.gui2-priority {{ margin-left: auto; color: var(--gui2-muted); font-size: 0.82rem; }}
.gui2-timeline {{ list-style: none; padding-left: 0; margin: 0; }}
.gui2-timeline li {{ display: grid; grid-template-columns: 120px 1fr; gap: var(--gui2-gap); padding: 10px 0; }}
.gui2-status {{ color: var(--gui2-muted); font-size: 0.84rem; }}
.gui2-flow-nodes, .gui2-variants, .gui2-comparison, .gui2-board {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--gui2-gap);
}}
.gui2-code {{
  overflow-x: auto; margin: 0; padding: var(--gui2-gap); border-radius: var(--gui2-radius);
  background: var(--gui2-code-bg); color: var(--gui2-code-text); font-size: 0.9rem;
}}
.gui2-code code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
.gui2-code-line {{ display: block; min-height: 1.4em; white-space: pre; }}
.gui2-code-line::before {{
  content: attr(data-line); display: inline-block; width: 3.5ch; margin-right: 12px; color: #9ca3af;
}}
.gui2-diff-line-add {{ background: #e9f7ee; }}
.gui2-diff-line-remove {{ background: #fdecec; }}
.gui2-diff-prefix {{ width: 3ch; color: var(--gui2-muted); }}
.gui2-preview {{
  white-space: pre-wrap; overflow-x: auto; padding: 12px; border-radius: calc(var(--gui2-radius) / 1.5);
  border: 1px solid var(--gui2-border); background: #fff; color: var(--gui2-muted);
}}
.gui2-form-input {{
  width: 100%; min-width: 120px; padding: 7px 8px; border: 1px solid var(--gui2-border);
  border-radius: 6px; background: #fff; color: var(--gui2-text); font: inherit;
}}
.gui2-actions {{ display: flex; flex-wrap: wrap; gap: 10px; padding-top: var(--gui2-gap); }}
.gui2-button {{
  border: 1.5px solid var(--gui2-border); border-radius: 7px; background: var(--gui2-text); color: #fff;
  padding: 8px 12px; font: inherit; cursor: pointer;
}}
.gui2-button.secondary {{ background: var(--gui2-surface); color: var(--gui2-text); }}
.gui2-sources {{ padding-left: 1.2rem; }}
.gui2-muted {{ color: var(--gui2-muted); }}
.gui2-card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--gui2-gap); }}
.gui2-chip-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
.gui2-sheet-panel {{ background: var(--gui2-surface); border: 1.5px solid var(--gui2-border); border-radius: var(--gui2-radius); padding: calc(var(--gui2-gap) * 1.2); box-shadow: 8px 8px 0 rgba(196,61,43,.13); }}
.gui2-sheet-panel.accent {{ background: #fff7dc; }}
.gui2-split {{ display: grid; gap: var(--gui2-gap); grid-template-columns: 1fr 1fr; }}
.gui2-split-left {{ grid-template-columns: 1.35fr .65fr; }}
.gui2-split-right {{ grid-template-columns: .65fr 1.35fr; }}
.gui2-tabs {{ border: 1.5px solid var(--gui2-border); border-radius: var(--gui2-radius); background: var(--gui2-surface); overflow: clip; }}
.gui2-tablist {{ display: flex; flex-wrap: wrap; gap: 0; border-bottom: 1.5px solid var(--gui2-border); }}
.gui2-tab {{ appearance: none; border: 0; border-right: 1px solid var(--gui2-border); background: transparent; color: var(--gui2-text); padding: 10px 13px; cursor: pointer; }}
.gui2-tab[aria-selected="true"] {{ background: var(--gui2-text); color: #fff; }}
.gui2-tab-badge {{ margin-left: 8px; color: var(--gui2-gold); }}
.gui2-tab-panels {{ padding: var(--gui2-gap); }}
.gui2-filter-label {{ display: grid; gap: 6px; max-width: 340px; margin-bottom: var(--gui2-gap); }}
.gui2-diagram-layout {{ display: grid; grid-template-columns: minmax(360px, 1.4fr) minmax(220px, .6fr); gap: var(--gui2-gap); }}
.gui2-diagram-canvas {{ position: relative; min-height: 360px; border: 1.5px solid var(--gui2-border); border-radius: var(--gui2-radius); background: #fffdf6; overflow: hidden; }}
.gui2-diagram-canvas::before {{ content: ""; position: absolute; inset: 0; background: linear-gradient(rgba(36,88,166,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(36,88,166,.08) 1px, transparent 1px); background-size: 24px 24px; }}
.gui2-diagram-node {{ position: absolute; z-index: 1; transform: translate(-50%, -50%); border: 1.5px solid var(--gui2-border); border-radius: 8px; background: #fffdf6; color: var(--gui2-text); padding: 8px 10px; box-shadow: 5px 5px 0 rgba(36,88,166,.18); cursor: pointer; }}
.gui2-diagram-node[aria-pressed="true"] {{ background: var(--gui2-blueprint); color: #fff; }}
.gui2-inspector {{ border: 1.5px solid var(--gui2-border); border-radius: var(--gui2-radius); padding: var(--gui2-gap); background: var(--gui2-surface); }}
.gui2-sandbox-shell iframe {{ width: 100%; min-height: 380px; border: 1.5px solid var(--gui2-border); border-radius: var(--gui2-radius); background: var(--gui2-surface); box-shadow: 8px 8px 0 rgba(39,35,29,.11); }}
.gui2-token-group + .gui2-token-group {{ margin-top: var(--gui2-gap); }}
.gui2-token {{ border: 1.5px solid var(--gui2-border); border-radius: var(--gui2-radius); padding: var(--gui2-gap); background: var(--gui2-surface); }}
.gui2-token-swatch {{ width: 100%; height: 36px; border: 1px dashed var(--gui2-border); border-radius: 6px; background: linear-gradient(135deg, #fffdf6, #e8ddca); }}
.gui2-component-matrix {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: var(--gui2-gap); }}
.gui2-variant-cell:has(.gui2-badge) {{ outline: 3px solid rgba(196,61,43,.2); }}
.gui2-slide-deck {{ border: 1.5px solid var(--gui2-border); border-radius: var(--gui2-radius); background: #fffdf6; overflow: clip; }}
.gui2-slide-toolbar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px; border-bottom: 1.5px solid var(--gui2-border); }}
.gui2-slide {{ min-height: 280px; padding: clamp(24px, 6vw, 64px); }}
.gui2-slide h3 {{ font: 500 clamp(2rem, 5vw, 4.4rem)/1 "Iowan Old Style", "Palatino Linotype", Georgia, serif; }}
.gui2-slide-notes {{ border-left: 4px solid var(--gui2-accent); padding-left: 12px; color: var(--gui2-muted); }}
.gui2-chart-panel {{ display: grid; gap: 10px; }}
.gui2-chart-row {{ display: grid; grid-template-columns: 120px 1fr 70px; gap: 12px; align-items: center; }}
.gui2-chart-track {{ height: 18px; border: 1px solid var(--gui2-border); background: var(--gui2-surface); border-radius: 999px; overflow: hidden; }}
.gui2-chart-track i {{ display: block; height: 100%; background: var(--gui2-accent); }}
.gui2-log-timeline {{ list-style: none; padding: 0; display: grid; gap: 8px; }}
.gui2-log-event {{ display: grid; grid-template-columns: 92px 80px 1fr; gap: 10px; padding: 10px; border: 1px solid var(--gui2-border); border-radius: 7px; background: var(--gui2-surface); }}
.gui2-log-error {{ border-color: var(--gui2-danger); }}
@container (max-width: 720px) {{
  .gui2-split, .gui2-diagram-layout {{ grid-template-columns: 1fr; }}
  .gui2-chart-row, .gui2-log-event {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 680px) {{
  .gui2-shell {{ padding: 18px; }}
  .gui2-timeline li {{ grid-template-columns: 1fr; gap: 2px; }}
  .gui2-split, .gui2-diagram-layout {{ grid-template-columns: 1fr; }}
  table {{ min-width: 480px; }}
}}
@media print {{
  body {{ background: #fff; }}
  .gui2-shell {{ max-width: none; padding: 0; }}
  .gui2-actions {{ display: none; }}
  .gui2-section {{ break-inside: avoid; }}
}}
""".strip()
