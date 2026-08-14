class AuthorProbe extends HTMLElement {
  connectedCallback() {
    this.dataset.hedronElement = "ext-author-probe";
  }
}

if (!customElements.get("ext-author-probe")) {
  customElements.define("ext-author-probe", AuthorProbe);
}
"""ext-author-probe — PLUGIN-040 external consumer element."""

class ExtAuthorProbe extends HTMLElement {
  connectedCallback() {
    if (!this.hasAttribute("status")) {
      this.setAttribute("status", "ready");
    }
  }
}

if (!customElements.get("ext-author-probe")) {
  customElements.define("ext-author-probe", ExtAuthorProbe);
}
