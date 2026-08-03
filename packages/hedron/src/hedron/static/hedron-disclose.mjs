/**
 * hedron-disclose — minimal HTMX-safe custom element.
 * Light DOM; reinits cleanly across HTMX swaps without duplicate listeners.
 */
class HedronDisclose extends HTMLElement {
  static observedAttributes = ["open", "label"];

  #onToggle = null;

  connectedCallback() {
    this.#ensureStructure();
    this.#sync();
    this.#bind();
  }

  disconnectedCallback() {
    this.#unbind();
  }

  attributeChangedCallback() {
    if (this.isConnected) {
      this.#sync();
    }
  }

  #unbind() {
    const btn = this.querySelector(":scope > [data-hedron-disclose-btn]");
    if (btn && this.#onToggle) {
      btn.removeEventListener("click", this.#onToggle);
    }
    this.#onToggle = null;
  }

  #bind() {
    this.#unbind();
    const btn = this.querySelector(":scope > [data-hedron-disclose-btn]");
    if (!btn) return;
    this.#onToggle = () => {
      const next = !(this.getAttribute("open") === "true");
      this.setAttribute("open", next ? "true" : "false");
      this.dispatchEvent(
        new CustomEvent("hedron-disclose", {
          bubbles: true,
          composed: false,
          detail: { open: next },
        }),
      );
    };
    btn.addEventListener("click", this.#onToggle);
  }

  #ensureStructure() {
    const btn = this.querySelector(":scope > [data-hedron-disclose-btn]");
    const panel = this.querySelector(":scope > [data-hedron-disclose-panel]");
    if (btn && panel) {
      return;
    }

    // Incomplete chrome: collect content nodes, dropping broken markers.
    const preserved = [];
    for (const node of Array.from(this.childNodes)) {
      if (
        node.nodeType === 1 &&
        (node.hasAttribute?.("data-hedron-disclose-btn") ||
          node.hasAttribute?.("data-hedron-disclose-panel"))
      ) {
        // Keep panel children if rebuilding a partial panel.
        if (node.hasAttribute?.("data-hedron-disclose-panel")) {
          preserved.push(...Array.from(node.childNodes));
        }
        continue;
      }
      preserved.push(node);
    }

    const nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.setAttribute("data-hedron-disclose-btn", "");

    const nextPanel = document.createElement("div");
    nextPanel.setAttribute("data-hedron-disclose-panel", "");

    this.replaceChildren();
    this.append(nextBtn, nextPanel);
    for (const node of preserved) {
      nextPanel.append(node);
    }
  }

  #sync() {
    const open = this.getAttribute("open") === "true";
    const label = this.getAttribute("label") || "Details";
    const btn = this.querySelector(":scope > [data-hedron-disclose-btn]");
    const panel = this.querySelector(":scope > [data-hedron-disclose-panel]");
    if (!(btn instanceof HTMLElement) || !(panel instanceof HTMLElement)) {
      return;
    }
    btn.textContent = label;
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) panel.removeAttribute("hidden");
    else panel.setAttribute("hidden", "");
  }

  rebind() {
    this.#ensureStructure();
    this.#sync();
    this.#bind();
  }
}

if (!customElements.get("hedron-disclose")) {
  customElements.define("hedron-disclose", HedronDisclose);
}

function rebindDisclose(root) {
  if (!(root instanceof Element)) return;
  const nodes = [];
  if (root.matches?.("hedron-disclose")) {
    nodes.push(root);
  }
  root.querySelectorAll?.("hedron-disclose").forEach((el) => nodes.push(el));
  for (const el of nodes) {
    if (el instanceof HedronDisclose) {
      el.rebind();
    }
  }
}

document.body.addEventListener("htmx:afterSwap", (event) => {
  rebindDisclose(event.target);
});
