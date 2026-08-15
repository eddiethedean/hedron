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
    track(this);
    this.#syncFormValue();
    this.addEventListener("change", () => this.#syncFormValue());
  }

  disconnectedCallback() {
    dispose(this);
  }

  #syncFormValue() {
    const values = [...this.querySelectorAll("input:checked")].map((el) => el.value);
    const fd = new FormData();
    for (const v of values) fd.append(this.getAttribute("name") || "choice", v);
    this.#internals?.setFormValue?.(fd);
  }
}

if (!customElements.get(TAG)) customElements.define(TAG, HedronFieldChoice);
