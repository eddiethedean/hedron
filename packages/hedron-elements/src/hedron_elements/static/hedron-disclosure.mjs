import { dispose, track } from "./hedron-bridge.mjs";

const TAG = "hedron-disclosure";

class HedronDisclosure extends HTMLElement {
  connectedCallback() {
    track(this);
    const details = this.querySelector("details");
    details?.addEventListener("toggle", () => {
      this.dispatchEvent(new CustomEvent("hedron-disclosure-change", { bubbles: true, detail: { open: details.open } }));
    });
  }

  disconnectedCallback() {
    dispose(this);
  }
}

if (!customElements.get(TAG)) customElements.define(TAG, HedronDisclosure);
