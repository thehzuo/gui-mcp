from __future__ import annotations

import argparse
import json
from pathlib import Path

from web_gui_mcp.render.artifact import render_artifact_to_html
from web_gui_mcp.schema.artifact import ArtifactSpec
from web_gui_mcp.schema.tool_io import RenderOptions


def render_example_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render an ArtifactSpec JSON file to HTML.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--interactivity", choices=["none", "local", "host_intents"], default="none")
    args = parser.parse_args(argv)

    spec = ArtifactSpec.model_validate(json.loads(args.input.read_text(encoding="utf-8")))
    rendered = render_artifact_to_html(
        spec,
        RenderOptions(
            delivery="static_html",
            interactivity=args.interactivity,
            density=spec.density,
            theme=spec.theme,
            include_runtime=args.interactivity != "none",
        ),
    )
    args.output.write_text(rendered.html, encoding="utf-8")
    print(f"Wrote {args.output} ({rendered.byte_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(render_example_main())
