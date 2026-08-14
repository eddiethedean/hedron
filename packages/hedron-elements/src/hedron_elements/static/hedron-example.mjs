/**
 * hedron-example — 0.36 ABI probe (light DOM).
 * Controlled `status` + disposable local expanded UI. Not form-associated.
 */
import { dispose, track, validateEventDetail } from "./hedron-bridge.mjs";

const TAG = "hedron-example";
const EVENT = "hedron-example-change";

class HedronExample extends HTMLElement {
  static observedAttributes = ["status", "data-hedron-abi"];

  #signal = null;
  #onToggle = null;
  #expanded = false;

  connectedCallback() {
    this.#ensure();
    this.#signal = track(this);
    this.#bind();
    this.#sync();
    this.setAttribute("data-hedron-upgraded", "true");
  }

  disconnectedCallback() {
    this.#unbind();
    dispose(this);
    this.#signal = null;
  }

  attributeChangedCallback() {
    if (this.isConnected) this.#sync();
  }

  #ensure() {
    if (!this.querySelector(":scope > [data-hedron-server-region='content']")) {
      const p = document.createElement("p");
      p.setAttribute("data-hedron-server-region", "content");
      p.textContent = this.getAttribute("status") || "Ready";
      this.appendChild(p);
    }
    if (!this.querySelector(":scope > [data-hedron-local='toggle']")) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.setAttribute("data-hedron-local", "toggle");
      btn.textContent = "Details";
      this.appendChild(btn);
    }
    if (!this.querySelector(":scope > [data-hedron-local='panel']")) {
      const panel = document.createElement("div");
      panel.setAttribute("data-hedron-local", "panel");
      panel.hidden = true;
      panel.textContent = "Local-only panel (disposable).";
      this.appendChild(panel);
    }
  }

  #unbind() {
    const btn = this.querySelector(":scope > [data-hedron-local='toggle']");
    if (btn && this.#onToggle) btn.removeEventListener("click", this.#onToggle);
    this.#onToggle = null;
  }

  #bind() {
    this.#unbind();
    const btn = this.querySelector(":scope > [data-hedron-local='toggle']");
    if (!btn) return;
    this.#onToggle = () => {
      this.#expanded = !this.#expanded;
      this.#syncLocal();
      const detail = { expanded: this.#expanded, status: this.getAttribute("status") };
      if (!validateEventDetail(detail, ["expanded", "status"])) return;
      this.dispatchEvent(
        new CustomEvent(EVENT, { bubbles: true, composed: false, detail }),
      );
    };
    btn.addEventListener("click", this.#onToggle, { signal: this.#signal });
  }

  #sync() {
    const region = this.querySelector(":scope > [data-hedron-server-region='content']");
    if (region) region.textContent = this.getAttribute("status") || "Ready";
    this.#syncLocal();
  }

  #syncLocal() {
    const panel = this.querySelector(":scope > [data-hedron-local='panel']");
    const btn = this.querySelector(":scope > [data-hedron-local='toggle']");
    if (panel) panel.hidden = !this.#expanded;
    if (btn) btn.setAttribute("aria-expanded", this.#expanded ? "true" : "false");
  }
}

if (!customElements.get(TAG)) {
  customElements.define(TAG, HedronExample);
}

function enhance(root) {
  const nodes = [];
  if (root?.matches?.(TAG)) nodes.push(root);
  root?.querySelectorAll?.(TAG)?.forEach((el) => nodes.push(el));
  for (const el of nodes) {
    if (el instanceof HedronExample && el.isConnected) {
      el.connectedCallback();
    }
  }
}

document.addEventListener("htmx:afterSwap", (ev) => enhance(ev.target || document));
document.addEventListener("htmx:load", (ev) => enhance(ev.target || document));
