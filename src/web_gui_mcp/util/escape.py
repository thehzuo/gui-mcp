from __future__ import annotations

import json
from html import escape as html_escape
from typing import Any
from urllib.parse import urlparse


def h(value: Any) -> str:
    """Escape a value for HTML text content."""
    return html_escape("" if value is None else str(value), quote=True)


def attr(value: Any) -> str:
    """Escape a value for an HTML attribute."""
    return h(value)


def attrs_to_html(**attrs: Any) -> str:
    rendered: list[str] = []
    for key, value in attrs.items():
        if value is None or value is False:
            continue
        name = key.rstrip("_").replace("_", "-")
        if value is True:
            rendered.append(f" {name}")
        else:
            rendered.append(f' {name}="{attr(value)}"')
    return "".join(rendered)


def tag(name: str, body: str = "", **attrs: Any) -> str:
    return f"<{name}{attrs_to_html(**attrs)}>{body}</{name}>"


def safe_json_script(value: Any) -> str:
    """Encode JSON for a non-executable script tag without allowing tag breakout."""
    if isinstance(value, str):
        raw = value
    else:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (
        raw.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def safe_href(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https", "mailto"}:
        return url
    if not parsed.scheme and url.startswith("#"):
        return url
    return None
