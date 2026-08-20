class SampleKitCallout extends HTMLElement {
  static get observedAttributes() {
    return ["status"];
  }

  connectedCallback() {
    this.dataset.hedronElement = "sample-kit-callout";
  }

  disconnectedCallback() {
    delete this.dataset.hedronElement;
  }

  attributeChangedCallback(name, previous, next) {
    if (previous === next) {
      return;
    }
    this.dispatchEvent(
      new CustomEvent("sample-kit-callout-change", {
        bubbles: true,
        detail: { attribute: name, value: next },
      }),
    );
  }
}

if (!customElements.get("sample-kit-callout")) {
  customElements.define("sample-kit-callout", SampleKitCallout);
}
