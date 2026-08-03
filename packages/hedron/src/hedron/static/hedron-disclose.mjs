/**
 * hedron-disclose — minimal HTMX-safe custom element.
 * Light DOM; reinits cleanly across HTMX swaps without duplicate listeners.
 */
class HedronDisclose extends HTMLElement {
  static observedAttributes = ["open", "label"];

  #onToggle = null;

  connectedCallback() {
    this.#render();
    this.#bind();
  }

  disconnectedCallback() {
    this.#unbind();
  }

  attributeChangedCallback() {
    if (this.isConnected) {
      this.#render();
    }
  }

  #unbind() {
    const btn = this.querySelector("[data-hedron-disclose-btn]");
    if (btn && this.#onToggle) {
      btn.removeEventListener("click", this.#onToggle);
    }
    this.#onToggle = null;
  }

  #bind() {
    this.#unbind();
    const btn = this.querySelector("[data-hedron-disclose-btn]");
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

  #render() {
    const open = this.getAttribute("open") === "true";
    const label = this.getAttribute("label") || "Details";
    const panel = this.querySelector("[data-hedron-disclose-panel]");
    const btn = this.querySelector("[data-hedron-disclose-btn]");
    if (!btn || !panel) {
      this.innerHTML = `
        <button type="button" data-hedron-disclose-btn aria-expanded="${open}">${label}</button>
        <div data-hedron-disclose-panel ${open ? "" : "hidden"}><slot></slot></div>
      `;
      return;
    }
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) panel.removeAttribute("hidden");
    else panel.setAttribute("hidden", "");
  }
}

if (!customElements.get("hedron-disclose")) {
  customElements.define("hedron-disclose", HedronDisclose);
}

// HTMX swap lifecycle: re-upgrade / re-bind after swaps
document.body.addEventListener("htmx:afterSwap", (event) => {
  const root = event.target;
  if (!(root instanceof Element)) return;
  root.querySelectorAll("hedron-disclose").forEach((el) => {
    if (el instanceof HedronDisclose) {
      el.disconnectedCallback();
      el.connectedCallback();
    }
  });
});
