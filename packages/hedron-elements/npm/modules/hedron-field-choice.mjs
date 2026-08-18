import { dispose, track } from "./hedron-bridge.mjs";

const TAG = "hedron-field-choice";

class HedronFieldChoice extends HTMLElement {
  static formAssociated = true;

  #internals;

  constructor() {
    super();
    this.#internals = this.attachInternals?.();
  }

  connectedCallback() {
    const signal = track(this);
    if (this.#internals) {
      this.querySelectorAll("input").forEach((el) => el.removeAttribute("name"));
    }
    this.#syncFormValue();
    this.addEventListener("change", () => this.#syncFormValue(), { signal });
  }

  disconnectedCallback() {
    dispose(this);
  }

  #syncFormValue() {
    const values = [...this.querySelectorAll("input:checked")].map((el) => el.value);
    const fd = new FormData();
    const name = this.getAttribute("name") || "choice";
    for (const v of values) fd.append(name, v);
    this.#internals?.setFormValue?.(fd);
  }
}

if (!customElements.get(TAG)) customElements.define(TAG, HedronFieldChoice);
