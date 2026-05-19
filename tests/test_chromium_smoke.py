from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from gui2_artifact_mcp.render.artifact import render_artifact_to_html
from gui2_artifact_mcp.schema.artifact import ArtifactSpec

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import Page, sync_playwright  # noqa: E402


def _render_page(tmp_path: Path, spec_payload: dict[str, Any]) -> Page:
    spec = ArtifactSpec.model_validate(spec_payload)
    html = render_artifact_to_html(spec).html
    path = tmp_path / "artifact.html"
    path.write_text(html, encoding="utf-8")
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(path.as_uri())
    page._gui2_browser = browser  # type: ignore[attr-defined]
    page._gui2_playwright = playwright  # type: ignore[attr-defined]
    return page


def _close_page(page: Page) -> None:
    page._gui2_browser.close()  # type: ignore[attr-defined]
    page._gui2_playwright.stop()  # type: ignore[attr-defined]


def test_chromium_tabs_filter_and_copy(tmp_path: Path) -> None:
    page = _render_page(
        tmp_path,
        {
            "v": "0.2",
            "artifact": "feature_explainer",
            "title": "Chrome smoke",
            "sections": [
                {
                    "kind": "tabs",
                    "title": "Tabs",
                    "tabs": [
                        {"id": "one", "label": "One", "body": "First panel."},
                        {"id": "two", "label": "Two", "body": "Second panel."},
                    ],
                },
                {
                    "kind": "filterable_collection",
                    "title": "Filter",
                    "items": [
                        {"id": "alpha", "title": "Alpha", "body": "Visible", "tags": ["keep"]},
                        {"id": "beta", "title": "Beta", "body": "Hidden", "tags": ["drop"]},
                    ],
                },
                {
                    "kind": "token_sheet",
                    "title": "Tokens",
                    "groups": [{"title": "Copy", "tokens": [{"name": "accent", "value": "#c43d2b"}]}],
                },
            ],
        },
    )
    try:
        page.get_by_role("button", name="Two").click()
        assert page.locator("[data-gui2-panel='two']").is_visible()
        page.locator("[data-gui2-filter]").fill("keep")
        assert page.get_by_text("Alpha").is_visible()
        assert page.get_by_text("Beta").is_hidden()
        copy_button = page.get_by_role("button", name="Copy").first
        copy_button.click()
        page.wait_for_function(
            "(button) => button.getAttribute('data-gui2-copied') !== null",
            arg=copy_button.element_handle(),
        )
        assert copy_button.get_attribute("data-gui2-copied") in {"true", "false"}
    finally:
        _close_page(page)


def test_chromium_slide_navigation_and_mobile_layout(tmp_path: Path) -> None:
    page = _render_page(
        tmp_path,
        {
            "v": "0.2",
            "artifact": "slide_deck",
            "title": "Deck",
            "sections": [
                {
                    "kind": "slide_deck",
                    "title": "Slides",
                    "slides": [
                        {"id": "one", "title": "One", "body": "First"},
                        {"id": "two", "title": "Two", "body": "Second"},
                    ],
                }
            ],
        },
    )
    try:
        page.keyboard.press("ArrowRight")
        assert page.locator("[data-gui2-slide][data-slide-id='two']").is_visible()
        page.set_viewport_size({"width": 390, "height": 780})
        assert page.locator(".gui2-shell").bounding_box()["width"] <= 390
    finally:
        _close_page(page)


def test_chromium_sandbox_prototype_and_prompt_tuner(tmp_path: Path) -> None:
    page = _render_page(
        tmp_path,
        {
            "v": "0.2",
            "artifact": "prompt_tuner",
            "title": "Sandbox",
            "sections": [
                {
                    "kind": "prototype_flow",
                    "title": "Flow",
                    "screens": [
                        {"id": "a", "title": "A", "body": "Start"},
                        {"id": "b", "title": "B", "body": "End"},
                    ],
                    "links": [{"from": "a", "to": "b", "label": "Next"}],
                },
                {
                    "kind": "prompt_tuner",
                    "title": "Prompt",
                    "template": "Hello {{name}}",
                    "variables": [{"name": "name", "label": "Name", "value": "Ada"}],
                },
            ],
        },
    )
    try:
        iframe = page.locator("iframe").first
        assert iframe.get_attribute("sandbox") == "allow-scripts"
        frame = iframe.content_frame
        frame.get_by_role("button", name="Next").click()
        assert frame.get_by_text("End").is_visible()

        prompt_frame = page.locator("iframe").nth(1).content_frame
        assert "Hello Ada" in prompt_frame.locator("[data-prompt-preview]").text_content()
        prompt_frame.locator("[data-prompt-var='name']").fill("Grace")
        assert "Hello Grace" in prompt_frame.locator("[data-prompt-preview]").text_content()
    finally:
        _close_page(page)


def test_chromium_dependency_toggles_and_drag_reorder(tmp_path: Path) -> None:
    page = _render_page(
        tmp_path,
        {
            "v": "0.2",
            "artifact": "triage_board",
            "title": "Editor smoke",
            "sections": [
                {
                    "kind": "dependency_toggle_list",
                    "title": "Flags",
                    "toggles": [
                        {"id": "base", "label": "Base", "enabled": True},
                        {"id": "child", "label": "Child", "enabled": True, "depends_on": ["base"]},
                    ],
                },
                {
                    "kind": "board",
                    "title": "Board",
                    "columns": [
                        {"id": "now", "title": "Now", "cards": [{"id": "a", "title": "Card A"}]},
                        {"id": "cut", "title": "Cut", "cards": []},
                    ],
                },
            ],
        },
    )
    try:
        frame = page.locator("iframe").first.content_frame
        frame.get_by_label("Base").uncheck()
        assert frame.locator("[data-toggle-id='child']").get_attribute("data-blocked") == "true"
        page.locator("[data-gui2-card-id='a']").drag_to(page.locator("[data-gui2-column-id='cut']"))
        assert page.locator("[data-gui2-column-id='cut'] [data-gui2-card-id='a']").is_visible()
    finally:
        _close_page(page)
