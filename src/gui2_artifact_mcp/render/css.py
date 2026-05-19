from __future__ import annotations

from gui2_artifact_mcp.schema.artifact import Density, Theme


def render_css(theme: Theme = "neutral", density: Density = "normal") -> str:
    density_scale = {
        "compact": ("12px", "14px", "8px"),
        "normal": ("18px", "16px", "8px"),
        "presentation": ("24px", "18px", "8px"),
    }[density]
    theme_tokens = {
        "neutral": ("#f5f5f7", "#ffffff", "#1d1d1f", "#6e6e73"),
        "technical": ("#f5f7fb", "#ffffff", "#1d1d1f", "#5f6673"),
        "warm": ("#f7f2ec", "#ffffff", "#1d1d1f", "#74695f"),
        "mono": ("#f5f5f7", "#ffffff", "#1d1d1f", "#6e6e73"),
    }[theme]
    gap, font_size, radius = density_scale
    bg, surface, text, muted = theme_tokens
    return f"""
:root {{
  --gui2-bg: {bg};
  --gui2-surface: {surface};
  --gui2-elevated: #ffffff;
  --gui2-border: #d2d2d7;
  --gui2-text: {text};
  --gui2-muted: {muted};
  --gui2-good: #248a3d;
  --gui2-warning: #b26a00;
  --gui2-danger: #d70015;
  --gui2-info: #0066cc;
  --gui2-accent: #0071e3;
  --gui2-blueprint: #0071e3;
  --gui2-gold: #bf7d00;
  --gui2-radius: {radius};
  --gui2-gap: {gap};
  --gui2-font-size: {font_size};
  --gui2-code-bg: #1d1d1f;
  --gui2-code-text: #f5f5f7;
  --gui2-shadow: 0 1px 2px rgba(0, 0, 0, .04), 0 14px 32px rgba(0, 0, 0, .06);
  --gui2-shadow-soft: 0 1px 2px rgba(0, 0, 0, .05);
}}
* {{ box-sizing: border-box; }}
[hidden] {{ display: none !important; }}
html {{ background: var(--gui2-bg); color: var(--gui2-text); }}
body {{
  margin: 0;
  font: 400 var(--gui2-font-size)/1.56 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
  letter-spacing: 0;
  background: var(--gui2-bg);
}}
a {{ color: var(--gui2-info); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
p {{
  margin: 0;
  max-width: 72ch;
  line-height: 1.68;
}}
p + p {{ margin-top: 0.85em; }}
strong + p {{ margin-top: 0.35em; }}
.gui2-shell {{
  container-type: inline-size;
  max-width: 1240px; margin: 0 auto; padding: clamp(16px, 3vw, 34px);
}}
.gui2-header {{
  display: grid;
  gap: 10px;
  align-content: start;
  justify-items: start;
  text-align: left;
  margin-bottom: calc(var(--gui2-gap) * 1.1);
  padding: 10px 0 calc(var(--gui2-gap) * 1.1);
  border-bottom: 1px solid var(--gui2-border);
}}
.gui2-kicker {{
  display: flex; flex-wrap: wrap; justify-content: flex-start; gap: 8px; align-items: center; margin-bottom: 0;
  color: var(--gui2-muted); font-size: 0.78rem; letter-spacing: 0;
}}
.gui2-header h1 {{
  margin: 0; max-width: 24ch;
  font: 700 clamp(2.05rem, 4.4vw, 3.9rem)/1.04 -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif;
  letter-spacing: 0;
}}
.gui2-subtitle {{ margin: 0; max-width: 72ch; color: var(--gui2-muted); font-size: clamp(1rem, 1.5vw, 1.18rem); line-height: 1.5; }}
body[data-gui2-artifact="slide_deck"] .gui2-header,
body[data-gui2-density="presentation"] .gui2-header {{
  min-height: clamp(200px, 26vw, 300px);
  align-content: center;
  justify-items: center;
  text-align: center;
  border-bottom: 0;
}}
body[data-gui2-artifact="slide_deck"] .gui2-kicker,
body[data-gui2-density="presentation"] .gui2-kicker {{ justify-content: center; }}
body[data-gui2-artifact="slide_deck"] .gui2-header h1,
body[data-gui2-density="presentation"] .gui2-header h1 {{
  max-width: 18ch;
  font-size: clamp(2.8rem, 7vw, 5.8rem);
  line-height: 1.02;
}}
body[data-gui2-artifact="slide_deck"] .gui2-subtitle,
body[data-gui2-density="presentation"] .gui2-subtitle {{
  max-width: 62ch;
  font-size: clamp(1.1rem, 2vw, 1.55rem);
  line-height: 1.38;
}}
body[data-gui2-density="compact"] .gui2-shell {{ padding: 14px 18px; }}
body[data-gui2-density="compact"] .gui2-header {{
  gap: 6px;
  margin-bottom: var(--gui2-gap);
  padding-bottom: var(--gui2-gap);
}}
body[data-gui2-density="compact"] .gui2-header h1 {{ font-size: clamp(1.8rem, 3vw, 2.8rem); }}
body[data-gui2-density="compact"] .gui2-card,
body[data-gui2-density="compact"] .gui2-callout,
body[data-gui2-density="compact"] .gui2-board-column {{
  box-shadow: none;
}}
.gui2-section {{
  display: grid;
  gap: calc(var(--gui2-gap) * 0.95);
  padding: calc(var(--gui2-gap) * 1.05) 0;
  border-bottom: 1px solid color-mix(in srgb, var(--gui2-border), transparent 45%);
}}
.gui2-section:last-of-type {{ border-bottom: 0; }}
.gui2-section h2 {{
  margin: 0;
  font: 700 clamp(1.28rem, 2.2vw, 1.8rem)/1.12 -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif;
  letter-spacing: 0;
}}
.gui2-section h3 {{ margin: 0; font-size: 1.04rem; line-height: 1.25; letter-spacing: 0; }}
.gui2-grid {{ display: grid; gap: var(--gui2-gap); }}
.gui2-summary-grid {{ grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
.gui2-card, .gui2-callout, .gui2-board-column {{
  display: grid;
  align-content: start;
  gap: calc(var(--gui2-gap) * 0.72);
  background: var(--gui2-surface);
  border: 1px solid color-mix(in srgb, var(--gui2-border), transparent 22%);
  border-left-width: 4px;
  border-radius: var(--gui2-radius);
  padding: var(--gui2-gap);
  box-shadow: var(--gui2-shadow-soft);
}}
.gui2-card p, .gui2-callout p, .gui2-sheet-panel p, .gui2-tab-panel p, .gui2-inspector p, .gui2-slide p {{
  color: var(--gui2-muted);
}}
.gui2-label {{ color: var(--gui2-muted); font-size: 0.82rem; margin-bottom: 4px; }}
.gui2-value {{ font-weight: 650; }}
.gui2-tone-good {{ border-left-color: var(--gui2-good); background: linear-gradient(90deg, rgba(36,138,61,.08), transparent 42px), var(--gui2-surface); }}
.gui2-tone-warning {{ border-left-color: var(--gui2-warning); background: linear-gradient(90deg, rgba(178,106,0,.09), transparent 42px), var(--gui2-surface); }}
.gui2-tone-danger {{ border-left-color: var(--gui2-danger); background: linear-gradient(90deg, rgba(215,0,21,.08), transparent 42px), var(--gui2-surface); }}
.gui2-tone-info {{ border-left-color: var(--gui2-info); background: linear-gradient(90deg, rgba(0,102,204,.08), transparent 42px), var(--gui2-surface); }}
.gui2-badge {{
  display: inline-flex; align-items: center; min-height: 24px; padding: 3px 10px;
  border: 1px solid var(--gui2-border); border-radius: 999px; background: rgba(255,255,255,.72);
  color: var(--gui2-muted); font-size: 0.78rem; backdrop-filter: saturate(180%) blur(14px);
}}
.gui2-table-wrap {{ overflow-x: auto; border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); background: var(--gui2-elevated); }}
table {{ width: 100%; border-collapse: collapse; min-width: 520px; background: var(--gui2-elevated); line-height: 1.5; }}
th, td {{ padding: 11px 12px; border-bottom: 1px solid var(--gui2-border); text-align: left; vertical-align: top; }}
th {{ background: #fbfbfd; font-size: 0.84rem; color: var(--gui2-muted); }}
tr:last-child td {{ border-bottom: 0; }}
.gui2-list {{ margin: 0; padding-left: 1.2rem; line-height: 1.58; }}
.gui2-list li + li {{ margin-top: 8px; }}
.gui2-checklist {{ list-style: none; padding-left: 0; margin: 0; }}
.gui2-checklist li {{ display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; }}
.gui2-priority {{ margin-left: auto; color: var(--gui2-muted); font-size: 0.82rem; }}
.gui2-timeline {{ list-style: none; padding-left: 0; margin: 0; }}
.gui2-timeline li {{ display: grid; grid-template-columns: 120px 1fr; gap: var(--gui2-gap); padding: 10px 0; }}
.gui2-status {{ color: var(--gui2-muted); font-size: 0.84rem; }}
.gui2-flow-nodes, .gui2-variants, .gui2-comparison, .gui2-board {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--gui2-gap);
}}
.gui2-board-column {{
  background: #fbfbfd;
  min-height: 180px;
}}
.gui2-board-column h3 {{
  color: var(--gui2-muted);
  font-size: .86rem;
  text-transform: uppercase;
  letter-spacing: .04em;
}}
[data-gui2-drag-card] {{
  cursor: grab;
  transition: box-shadow .18s ease, border-color .18s ease;
}}
[data-gui2-drag-card]:hover {{
  box-shadow: var(--gui2-shadow);
}}
[data-gui2-drag-card]:active {{ cursor: grabbing; }}
[data-gui2-drop-zone][data-gui2-drag-over="true"] {{
  outline: 2px dashed var(--gui2-accent);
  outline-offset: 4px;
  background: rgba(0,113,227,.05);
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
.gui2-section-diff_review table {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: .86rem;
}}
.gui2-section-diff_review td:nth-child(2) {{
  width: 6ch;
  color: var(--gui2-muted);
  text-align: right;
  background: #fbfbfd;
}}
.gui2-diff-line-add {{ background: #e9f7ee; }}
.gui2-diff-line-remove {{ background: #fdecec; }}
.gui2-diff-prefix {{ width: 3ch; color: var(--gui2-muted); }}
.gui2-preview {{
  white-space: pre-wrap; overflow-x: auto; padding: 12px; border-radius: calc(var(--gui2-radius) / 1.5);
  border: 1px solid var(--gui2-border); background: #fbfbfd; color: var(--gui2-muted);
}}
.gui2-form-input {{
  width: 100%; min-width: 120px; padding: 10px 12px; border: 1px solid var(--gui2-border);
  border-radius: 8px; background: #fff; color: var(--gui2-text); font: inherit;
}}
.gui2-actions {{ display: flex; flex-wrap: wrap; gap: 10px; padding-top: var(--gui2-gap); }}
.gui2-button {{
  border: 1px solid var(--gui2-accent); border-radius: 999px; background: var(--gui2-accent); color: #fff;
  padding: 9px 16px; font: inherit; cursor: pointer;
}}
.gui2-button:hover {{ background: #147ce5; border-color: #147ce5; }}
.gui2-button:focus-visible, .gui2-tab:focus-visible, .gui2-diagram-node:focus-visible, .gui2-form-input:focus-visible {{
  outline: 3px solid rgba(0,113,227,.25);
  outline-offset: 2px;
}}
.gui2-button.secondary {{ background: transparent; color: var(--gui2-info); }}
.gui2-button.secondary:hover {{ background: rgba(0,113,227,.08); }}
.gui2-sources {{ padding-left: 1.2rem; }}
.gui2-muted {{ color: var(--gui2-muted); }}
.gui2-card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--gui2-gap); }}
.gui2-chip-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
.gui2-sheet-panel {{ display: grid; align-content: start; gap: calc(var(--gui2-gap) * 0.72); background: var(--gui2-surface); border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); padding: calc(var(--gui2-gap) * 1.2); box-shadow: var(--gui2-shadow-soft); }}
.gui2-sheet-panel.accent {{ background: #fbfbfd; }}
.gui2-split {{ display: grid; gap: var(--gui2-gap); grid-template-columns: 1fr 1fr; }}
.gui2-split-left {{ grid-template-columns: 1.35fr .65fr; }}
.gui2-split-right {{ grid-template-columns: .65fr 1.35fr; }}
.gui2-tabs {{ border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); background: var(--gui2-surface); overflow: clip; box-shadow: var(--gui2-shadow-soft); }}
.gui2-tablist {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 10px; border-bottom: 1px solid var(--gui2-border); background: #fbfbfd; }}
.gui2-tab {{ appearance: none; border: 1px solid transparent; border-radius: 999px; background: transparent; color: var(--gui2-text); padding: 8px 13px; cursor: pointer; }}
.gui2-tab:hover {{ background: rgba(0,113,227,.08); }}
.gui2-tab[aria-selected="true"] {{ background: var(--gui2-text); color: #fff; }}
.gui2-tab-badge {{ margin-left: 8px; color: var(--gui2-gold); }}
.gui2-tab-panels {{ padding: var(--gui2-gap); }}
.gui2-tab-panel {{ display: grid; gap: calc(var(--gui2-gap) * 0.72); align-content: start; }}
.gui2-filter-label {{ display: grid; gap: 6px; max-width: 340px; margin-bottom: var(--gui2-gap); }}
.gui2-diagram-layout {{ display: grid; grid-template-columns: minmax(360px, 1.4fr) minmax(260px, .6fr); gap: var(--gui2-gap); }}
.gui2-diagram-canvas {{ position: relative; min-height: 360px; border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); background: linear-gradient(180deg, #fff, #fbfbfd); overflow: hidden; }}
.gui2-diagram-canvas::before {{ content: ""; position: absolute; inset: 0; background: radial-gradient(circle at center, rgba(0,113,227,.08) 0 1px, transparent 1px); background-size: 26px 26px; }}
.gui2-diagram-edges {{ position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }}
.gui2-diagram-edges line {{ stroke: rgba(0,102,204,.42); stroke-width: .42; vector-effect: non-scaling-stroke; }}
.gui2-diagram-node {{ position: absolute; z-index: 2; transform: translate(-50%, -50%); border: 1px solid var(--gui2-border); border-radius: 999px; background: #fff; color: var(--gui2-text); padding: 8px 12px; box-shadow: 0 10px 24px rgba(0,0,0,.09); cursor: pointer; transition: transform .18s ease, box-shadow .18s ease, background .18s ease; }}
.gui2-diagram-node:hover {{ transform: translate(-50%, -52%); box-shadow: var(--gui2-shadow); }}
.gui2-diagram-node[aria-pressed="true"] {{ background: var(--gui2-blueprint); color: #fff; }}
.gui2-inspector {{ display: grid; align-content: start; gap: calc(var(--gui2-gap) * 0.72); border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); padding: var(--gui2-gap); background: var(--gui2-surface); box-shadow: var(--gui2-shadow-soft); }}
.gui2-sandbox-shell iframe {{ width: 100%; min-height: 380px; border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); background: var(--gui2-surface); box-shadow: var(--gui2-shadow-soft); }}
.gui2-token-group + .gui2-token-group {{ margin-top: var(--gui2-gap); }}
.gui2-token {{ display: grid; align-content: start; gap: calc(var(--gui2-gap) * 0.72); border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); padding: var(--gui2-gap); background: var(--gui2-surface); box-shadow: var(--gui2-shadow-soft); }}
.gui2-token-swatch {{ width: 100%; height: 36px; border: 1px solid var(--gui2-border); border-radius: 8px; background: linear-gradient(135deg, #fff, #e8e8ed); }}
.gui2-component-matrix {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: var(--gui2-gap); }}
.gui2-component-preview {{
  display: grid;
  min-height: 86px;
  align-items: center;
  justify-items: center;
  border: 1px solid var(--gui2-border);
  border-radius: var(--gui2-radius);
  background: #fbfbfd;
}}
.gui2-component-specimen {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 132px;
  min-height: 40px;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--gui2-accent);
  background: var(--gui2-accent);
  color: #fff;
  font-weight: 650;
}}
.gui2-component-specimen[data-state*="disabled" i] {{
  border-color: var(--gui2-border);
  background: #e8e8ed;
  color: var(--gui2-muted);
}}
.gui2-component-specimen[data-intent*="secondary" i] {{
  background: transparent;
  color: var(--gui2-info);
}}
.gui2-variant-cell:has(.gui2-badge) {{ outline: 3px solid rgba(0,113,227,.18); }}
.gui2-slide-deck {{ border: 1px solid var(--gui2-border); border-radius: var(--gui2-radius); background: #fff; overflow: clip; box-shadow: var(--gui2-shadow); }}
.gui2-slide-toolbar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px; border-bottom: 1px solid var(--gui2-border); background: #fbfbfd; }}
.gui2-slide {{ display: grid; align-content: center; gap: calc(var(--gui2-gap) * 0.9); aspect-ratio: 16 / 9; min-height: 280px; padding: clamp(24px, 6vw, 64px); }}
.gui2-slide h3 {{ font: 700 clamp(2rem, 5vw, 4.4rem)/1.04 -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif; }}
.gui2-slide-notes {{ border-left: 4px solid var(--gui2-accent); padding-left: 12px; color: var(--gui2-muted); line-height: 1.62; }}
.gui2-chart-panel {{ display: grid; gap: 10px; }}
.gui2-chart-row {{ display: grid; grid-template-columns: 120px 1fr 70px; gap: 12px; align-items: center; }}
.gui2-chart-track {{ height: 18px; border: 1px solid var(--gui2-border); background: var(--gui2-surface); border-radius: 999px; overflow: hidden; }}
.gui2-chart-track i {{ display: block; height: 100%; background: var(--gui2-accent); }}
.gui2-log-timeline {{ list-style: none; padding: 0; display: grid; gap: 8px; }}
.gui2-log-event {{ display: grid; grid-template-columns: 92px 80px 1fr; gap: 10px; padding: 10px; border: 1px solid var(--gui2-border); border-radius: 8px; background: var(--gui2-surface); }}
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
