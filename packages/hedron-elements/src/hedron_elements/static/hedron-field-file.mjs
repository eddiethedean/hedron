import { dispose, track } from "./hedron-bridge.mjs";

const TAG = "hedron-field-file";

class HedronFieldFile extends HTMLElement {
  static formAssociated = true;

  #internals;

  constructor() {
    super();
    this.#internals = this.attachInternals?.();
  }

  connectedCallback() {
    track(this);
    const input = this.querySelector("input[type='file']");
    input?.addEventListener("change", () => {
      this.#internals?.setFormValue?.(input.files);
    });
    track(this, { listener: input });
  }

  disconnectedCallback() {
    dispose(this);
  }
}

if (!customElements.get(TAG)) customElements.define(TAG, HedronFieldFile);
