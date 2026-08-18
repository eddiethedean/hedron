import { dispose, track } from "./hedron-bridge.mjs";
import { InteractionState, bindHtmxInteractionState } from "./interaction-state.mjs";

const TAG = "hedron-action-async";

class HedronActionAsync extends HTMLElement {
  #machine = new InteractionState({ policy: "replace" });
  #unbind = null;

  connectedCallback() {
    const signal = track(this);
    this.setAttribute("aria-live", "polite");
    this.#unbind = bindHtmxInteractionState(this, this.#machine);
    const btn = this.querySelector("button");
    btn?.addEventListener("click", () => {
      this.dispatchEvent(
        new CustomEvent("hedron-action-change", {
          bubbles: true,
          detail: { state: this.#machine.state },
        }),
      );
    }, { signal });
  }

  disconnectedCallback() {
    this.#unbind?.();
    dispose(this);
  }
}

if (!customElements.get(TAG)) customElements.define(TAG, HedronActionAsync);
