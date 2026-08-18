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
    const signal = track(this);
    const input = this.querySelector("input[type='file']");
    if (this.#internals) input?.removeAttribute("name");
    input?.addEventListener(
      "change",
      () => {
        if (!input.files || input.files.length === 0) {
          this.#internals?.setFormValue?.(null);
          return;
        }
        const fd = new FormData();
        const name = this.getAttribute("name") || "file";
        for (const file of input.files) fd.append(name, file);
        this.#internals?.setFormValue?.(fd);
      },
      { signal },
    );
  }

  disconnectedCallback() {
    dispose(this);
  }
}

if (!customElements.get(TAG)) customElements.define(TAG, HedronFieldFile);
