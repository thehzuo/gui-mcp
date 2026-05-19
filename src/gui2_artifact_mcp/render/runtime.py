from __future__ import annotations


def render_runtime_js() -> str:
    return """
(() => {
  const state = document.querySelector("#artifact-state");
  const setCopied = (button, ok = true) => {
    button.dataset.gui2Copied = ok ? "true" : "false";
    const original = button.dataset.gui2OriginalLabel || button.textContent;
    button.dataset.gui2OriginalLabel = original;
    if (ok) {
      button.textContent = "Copied";
      window.setTimeout(() => { button.textContent = original; }, 900);
    }
  };
  const readPayload = (button) => {
    const raw = button.getAttribute("data-gui2-payload");
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return raw; }
  };
  const copyText = async (text) => {
    if (!navigator.clipboard) return false;
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  };
  const activateTab = (root, id) => {
    root.querySelectorAll("[data-gui2-tab]").forEach((tab) => {
      tab.setAttribute("aria-selected", String(tab.dataset.gui2Tab === id));
    });
    root.querySelectorAll("[data-gui2-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.gui2Panel !== id;
    });
  };
  const activateSlide = (deck, index) => {
    const slides = [...deck.querySelectorAll("[data-gui2-slide]")];
    if (!slides.length) return;
    const next = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== next; });
    deck.dataset.gui2SlideIndex = String(next);
    const count = deck.querySelector("[data-gui2-slide-count]");
    if (count) count.textContent = `${next + 1} / ${slides.length}`;
  };
  const inspectNode = (inspect) => {
    const root = inspect.closest("[data-gui2-diagram]");
    root.querySelector("[data-gui2-inspector-title]").textContent = inspect.dataset.gui2Title || "";
    root.querySelector("[data-gui2-inspector-body]").textContent = inspect.dataset.gui2Body || "";
    root.querySelectorAll("[data-gui2-inspect]").forEach((node) => {
      node.setAttribute("aria-pressed", String(node === inspect));
    });
  };
  document.querySelectorAll("[data-gui2-tabs]").forEach((root) => {
    const first = root.querySelector("[data-gui2-tab][aria-selected='true']") || root.querySelector("[data-gui2-tab]");
    if (first) activateTab(root, first.dataset.gui2Tab);
  });
  document.querySelectorAll("[data-gui2-slide-deck]").forEach((deck) => activateSlide(deck, 0));
  document.querySelectorAll("[data-gui2-diagram]").forEach((diagram) => {
    const first = diagram.querySelector("[data-gui2-inspect]");
    if (first) inspectNode(first);
  });
  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-gui2-action]");
    const tab = event.target.closest("[data-gui2-tab]");
    const inspect = event.target.closest("[data-gui2-inspect]");
    const slideControl = event.target.closest("[data-gui2-slide-control]");
    if (tab) {
      activateTab(tab.closest("[data-gui2-tabs]"), tab.dataset.gui2Tab);
      return;
    }
    if (inspect) {
      inspectNode(inspect);
      return;
    }
    if (slideControl) {
      const deck = slideControl.closest("[data-gui2-slide-deck]");
      const current = Number(deck.dataset.gui2SlideIndex || 0);
      activateSlide(deck, current + (slideControl.dataset.gui2SlideControl === "next" ? 1 : -1));
      return;
    }
    if (!button) return;
    const action = button.getAttribute("data-gui2-action");
    if (action === "copy-json") {
      setCopied(button, await copyText(state ? state.textContent : "{}"));
    } else if (action === "copy-markdown" || action === "copy-prompt") {
      const payload = readPayload(button);
      setCopied(button, await copyText(typeof payload === "string" ? payload : JSON.stringify(payload, null, 2)));
    } else if (action === "copy-payload") {
      const payload = readPayload(button);
      setCopied(button, await copyText(typeof payload === "string" ? payload : JSON.stringify(payload, null, 2)));
    } else if (action === "emit-intent") {
      window.parent.postMessage({ type: "gui2.intent", payload: readPayload(button) }, "*");
    }
  });
  document.addEventListener("input", (event) => {
    const filter = event.target.closest("[data-gui2-filter]");
    if (!filter) return;
    const root = filter.closest("[data-gui2-filter-root]");
    const query = filter.value.trim().toLowerCase();
    root.querySelectorAll("[data-gui2-filter-item]").forEach((item) => {
      item.hidden = query && !item.dataset.gui2FilterText.includes(query);
    });
  });
  document.addEventListener("keydown", (event) => {
    const deck = event.target.closest("[data-gui2-slide-deck]") || document.querySelector("[data-gui2-slide-deck]");
    if (!deck) return;
    if (event.key === "ArrowRight") {
      activateSlide(deck, Number(deck.dataset.gui2SlideIndex || 0) + 1);
    } else if (event.key === "ArrowLeft") {
      activateSlide(deck, Number(deck.dataset.gui2SlideIndex || 0) - 1);
    }
  });
  let dragged = null;
  document.addEventListener("dragstart", (event) => {
    dragged = event.target.closest("[data-gui2-drag-card]");
    if (dragged) event.dataTransfer.setData("text/plain", dragged.dataset.gui2CardId || "");
  });
  document.addEventListener("dragover", (event) => {
    if (event.target.closest("[data-gui2-drop-zone]")) event.preventDefault();
  });
  document.addEventListener("drop", (event) => {
    const zone = event.target.closest("[data-gui2-drop-zone]");
    if (!zone || !dragged) return;
    event.preventDefault();
    zone.appendChild(dragged);
    window.dispatchEvent(new CustomEvent("gui2:state-changed", { detail: { kind: "drag_reorder" } }));
  });
})();
""".strip()


def render_runtime_tag(include_runtime: bool) -> str:
    if not include_runtime:
        return ""
    return f"<script>{render_runtime_js()}</script>"


def render_sandbox_runtime_js() -> str:
    return """
(() => {
  const post = (type, payload) => window.parent.postMessage({ type, payload }, "*");
  const copyText = async (text, button) => {
    let ok = false;
    if (navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(text);
        ok = true;
      } catch {
        ok = false;
      }
    }
    if (button) button.dataset.gui2Copied = ok ? "true" : "false";
    post("gui2.copy_requested", { ok, text });
  };
  const showScreen = (id) => {
    document.querySelectorAll("[data-screen]").forEach((screen) => {
      screen.hidden = screen.dataset.screen !== id;
    });
  };
  const renderPrompt = () => {
    const template = document.querySelector("[data-prompt-template]");
    const preview = document.querySelector("[data-prompt-preview]");
    if (!template || !preview) return;
    let text = template.value;
    document.querySelectorAll("[data-prompt-var]").forEach((input) => {
      text = text.replaceAll(`{{${input.dataset.promptVar}}}`, input.value);
    });
    preview.textContent = text;
    post("gui2.state_changed", { kind: "live_template_render" });
  };
  const updateDependencies = () => {
    document.querySelectorAll("[data-toggle-row]").forEach((row) => {
      const input = row.querySelector("input");
      const deps = (row.dataset.depends || "").split(",").filter(Boolean);
      const missing = deps.some((id) => {
        const dep = document.querySelector(`[data-toggle-id="${CSS.escape(id)}"] input`);
        return dep && !dep.checked;
      });
      row.dataset.blocked = String(missing && input.checked);
    });
    post("gui2.state_changed", { kind: "toggle_with_dependencies" });
  };
  document.addEventListener("click", async (event) => {
    const target = event.target.closest("[data-prototype-target]");
    const replay = event.target.closest("[data-animation-replay]");
    const step = event.target.closest("[data-step-duration]");
    const copy = event.target.closest("[data-copy]");
    if (target) showScreen(target.dataset.prototypeTarget);
    if (step) {
      const input = document.querySelector("[data-duration]");
      if (input) {
        input.value = String(Math.max(50, Math.min(5000, Number(input.value) + Number(step.dataset.stepDuration))));
        document.documentElement.style.setProperty("--duration", `${input.value}ms`);
      }
    }
    if (replay) {
      const puck = document.querySelector(".sandbox-puck");
      if (puck) {
        puck.classList.remove("run");
        void puck.offsetWidth;
        puck.classList.add("run");
      }
    }
    if (copy) await copyText(copy.dataset.copy || "", copy);
  });
  document.addEventListener("input", (event) => {
    if (event.target.matches("[data-duration]")) {
      document.documentElement.style.setProperty("--duration", `${event.target.value}ms`);
    }
    if (event.target.matches("[data-prompt-template], [data-prompt-var]")) renderPrompt();
    if (event.target.closest("[data-toggle-row]")) updateDependencies();
  });
  showScreen(document.querySelector("[data-screen]")?.dataset.screen || "");
  renderPrompt();
  updateDependencies();
})();
""".strip()
