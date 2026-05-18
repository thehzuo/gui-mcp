from __future__ import annotations


def render_runtime_js() -> str:
    return """
(() => {
  const state = document.querySelector("#artifact-state");
  const readPayload = (button) => {
    const raw = button.getAttribute("data-gui2-payload");
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return raw; }
  };
  const copyText = async (text) => {
    if (!navigator.clipboard) return;
    await navigator.clipboard.writeText(text);
  };
  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-gui2-action]");
    if (!button) return;
    const action = button.getAttribute("data-gui2-action");
    if (action === "copy-json") {
      await copyText(state ? state.textContent : "{}");
    } else if (action === "copy-markdown" || action === "copy-prompt") {
      const payload = readPayload(button);
      await copyText(typeof payload === "string" ? payload : JSON.stringify(payload, null, 2));
    } else if (action === "emit-intent") {
      window.parent.postMessage({ type: "gui2.intent", payload: readPayload(button) }, "*");
    }
  });
})();
""".strip()


def render_runtime_tag(include_runtime: bool) -> str:
    if not include_runtime:
        return ""
    return f"<script>{render_runtime_js()}</script>"
