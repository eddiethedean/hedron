import { dispose, track } from "./hedron-bridge.mjs";

const TAG = "hedron-dialog";

class HedronDialog extends HTMLElement {
  connectedCallback() {
    track(this);
    const dialog = this.querySelector("dialog");
    if (dialog && this.hasAttribute("open")) dialog.showModal();
  }

  disconnectedCallback() {
    dispose(this);
  }
}

if (!customElements.get(TAG)) customElements.define(TAG, HedronDialog);
