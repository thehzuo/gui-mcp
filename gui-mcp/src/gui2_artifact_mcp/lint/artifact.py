from __future__ import annotations

import re

from gui2_artifact_mcp.schema.limits import MAX_BODY_LENGTH, MAX_CODE_LENGTH, MAX_SECTIONS
from gui2_artifact_mcp.schema.tool_io import LintArtifactInput, LintArtifactOutput, LintIssue

RISKY_TEXT_RE = re.compile(r"(<\s*script|</\s*script|on[a-z]+\s*=|javascript:)", re.I)
INLINE_HANDLER_RE = re.compile(r"\son[a-z]+\s*=", re.I)
JAVASCRIPT_URL_RE = re.compile(r"javascript\s*:", re.I)


def lint_artifact_input(input_data: LintArtifactInput) -> LintArtifactOutput:
    issues: list[LintIssue] = []
    if input_data.spec is None and input_data.html is None:
        issues.append(
            LintIssue(
                check="schema",
                severity="error",
                message="Provide either spec or html.",
            )
        )
    for check in input_data.checks:
        if check == "schema":
            _lint_schema(input_data, issues)
        elif check == "security":
            _lint_security(input_data, issues)
        elif check == "html_size":
            _lint_html_size(input_data, issues)
        elif check == "accessibility":
            _lint_accessibility(input_data, issues)
        elif check == "mobile":
            _lint_mobile(input_data, issues)
        elif check == "token_cost":
            _lint_token_cost(input_data, issues)
    return LintArtifactOutput(
        ok=not any(issue.severity == "error" for issue in issues),
        issues=issues,
    )


def _lint_schema(input_data: LintArtifactInput, issues: list[LintIssue]) -> None:
    if input_data.spec is not None:
        issues.append(LintIssue(check="schema", severity="info", message="Spec is valid."))


def _lint_security(input_data: LintArtifactInput, issues: list[LintIssue]) -> None:
    if input_data.spec is not None:
        for path, value in _iter_strings(input_data.spec.model_dump(mode="json", by_alias=True)):
            if RISKY_TEXT_RE.search(value):
                issues.append(
                    LintIssue(
                        check="security",
                        severity="warning",
                        message="Spec contains text that will be escaped by the renderer.",
                        path=path,
                    )
                )
    if input_data.html is not None:
        if INLINE_HANDLER_RE.search(input_data.html):
            issues.append(
                LintIssue(
                    check="security",
                    severity="error",
                    message="HTML contains inline event-handler attributes.",
                )
            )
        if JAVASCRIPT_URL_RE.search(input_data.html):
            issues.append(
                LintIssue(
                    check="security",
                    severity="error",
                    message="HTML contains a javascript: URL.",
                )
            )


def _lint_html_size(input_data: LintArtifactInput, issues: list[LintIssue]) -> None:
    if input_data.html is not None:
        size = len(input_data.html.encode("utf-8"))
        if size > 500_000:
            issues.append(
                LintIssue(
                    check="html_size",
                    severity="warning",
                    message=f"HTML is large for an artifact response: {size} bytes.",
                )
            )


def _lint_accessibility(input_data: LintArtifactInput, issues: list[LintIssue]) -> None:
    if input_data.html is None:
        return
    if "<html lang=" not in input_data.html:
        issues.append(
            LintIssue(check="accessibility", severity="warning", message="HTML is missing lang.")
        )
    if "<h1>" not in input_data.html:
        issues.append(
            LintIssue(check="accessibility", severity="warning", message="HTML is missing h1.")
        )


def _lint_mobile(input_data: LintArtifactInput, issues: list[LintIssue]) -> None:
    if input_data.html is not None and 'name="viewport"' not in input_data.html:
        issues.append(
            LintIssue(check="mobile", severity="warning", message="HTML is missing viewport meta.")
        )


def _lint_token_cost(input_data: LintArtifactInput, issues: list[LintIssue]) -> None:
    if input_data.spec is None:
        return
    spec = input_data.spec
    if len(spec.sections) > MAX_SECTIONS * 0.75:
        issues.append(
            LintIssue(check="token_cost", severity="warning", message="Spec has many sections.")
        )
    for index, section in enumerate(spec.sections):
        body = getattr(section, "body", "")
        code = getattr(section, "code", "")
        if len(body) > MAX_BODY_LENGTH * 0.75:
            issues.append(
                LintIssue(
                    check="token_cost",
                    severity="warning",
                    message="Narrative body is close to maximum length.",
                    path=f"/sections/{index}/body",
                )
            )
        if len(code) > MAX_CODE_LENGTH * 0.75:
            issues.append(
                LintIssue(
                    check="token_cost",
                    severity="warning",
                    message="Code block is close to maximum length.",
                    path=f"/sections/{index}/code",
                )
            )


def _iter_strings(value: object, path: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, str):
        found.append((path, value))
    elif isinstance(value, dict):
        for key, child in value.items():
            found.extend(_iter_strings(child, f"{path}/{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_iter_strings(child, f"{path}/{index}"))
    return found
