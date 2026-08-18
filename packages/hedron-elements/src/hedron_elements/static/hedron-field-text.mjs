import { dispose, track } from "./hedron-bridge.mjs";

const TAG = "hedron-field-text";

class HedronFieldText extends HTMLElement {
  static formAssociated = true;
  static observedAttributes = ["name", "value", "required", "disabled"];

  #internals;
  #input;

  constructor() {
    super();
    this.#internals = this.attachInternals?.();
  }

  connectedCallback() {
    const signal = track(this);
    this.#ensure();
    this.#sync();
    this.#input.addEventListener("input", () => this.#publish(), { signal });
  }

  disconnectedCallback() {
    dispose(this);
  }

  attributeChangedCallback() {
    if (this.isConnected) this.#sync();
  }

  #ensure() {
    this.#input = this.querySelector("[data-hedron-server-region='control']");
    if (!this.#input) {
      this.#input = document.createElement("input");
      this.#input.setAttribute("data-hedron-server-region", "control");
      this.appendChild(this.#input);
    }
  }

  #sync() {
    const name = this.getAttribute("name") || "field";
    if (this.#internals) {
      this.#input.removeAttribute("name");
    } else {
      this.#input.name = name;
    }
    this.#input.value = this.getAttribute("value") || "";
    this.#input.required = this.hasAttribute("required");
    this.#input.disabled = this.hasAttribute("disabled");
    this.#publish();
  }

  #publish() {
    this.#internals?.setFormValue?.(this.#input.value);
  }
}

if (!customElements.get(TAG)) customElements.define(TAG, HedronFieldText);
