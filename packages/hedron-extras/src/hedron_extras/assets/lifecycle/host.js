/**
 * Shared light-DOM extras host (LIFECYCLE-051).
 * Existing ABI: observed attribute data-hedron-payload, htmx_lifecycle, no shadow DOM.
 */
const SUPPORTED_TAGS = [
  "hedron-extras-image-tools",
  "hedron-extras-calendar",
  "hedron-extras-signature",
  "hedron-extras-typeahead",
  "hedron-extras-composition",
];

class HedronExtrasHost extends HTMLElement {
  constructor() {
    super();
    this._ac = null;
    this._objectUrls = [];
    this._cleanups = [];
    this._revision = 0;
  }

  static get observedAttributes() {
    return ["data-hedron-payload"];
  }

  connectedCallback() {
    this._connect("connect");
  }

  disconnectedCallback() {
    this._disconnect();
  }

  attributeChangedCallback(name, previous, next) {
    if (name !== "data-hedron-payload" || previous === next) return;
    if (this.isConnected) this._connect("reconnect");
  }

  _parsePayload() {
    const raw = this.getAttribute("data-hedron-payload");
    if (!raw) return {};
    try {
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch {
      this.setAttribute("data-hedron-malformed", "1");
      this.setAttribute("role", "alert");
      return {};
    }
  }

  _connect(reason) {
    this._disconnect();
    this._revision += 1;
    const revision = this._revision;
    this._ac = new AbortController();
    this.dataset.hedronLifecycle = reason;
    this.dataset.hedronHost = "ready";
    this.removeAttribute("data-hedron-malformed");
    const payload = this._parsePayload();
    const signal = this._ac.signal;

    const onAbort = () => {
      if (revision !== this._revision) return;
    };
    signal.addEventListener("abort", onAbort);
    this._cleanups.push(() => signal.removeEventListener("abort", onAbort));

    const cancel = this.querySelector("[data-hedron-cancel]");
    if (cancel instanceof HTMLElement) {
      const onCancel = () => this._ac && this._ac.abort();
      cancel.addEventListener("click", onCancel);
      this._cleanups.push(() => cancel.removeEventListener("click", onCancel));
    }

    if (this.tagName.toLowerCase() === "hedron-extras-typeahead") {
      this._wireTypeahead(payload, signal, revision);
    }
  }

  _wireTypeahead(payload, signal, revision) {
    const input = this.querySelector("input[role='combobox']");
    if (!(input instanceof HTMLInputElement)) return;
    const source = typeof payload.source === "string" ? payload.source : "";
    if (!source || source.startsWith("javascript:")) return;
    let seq = 0;
    const onInput = () => {
      const requestId = ++seq;
      const controller = new AbortController();
      const onParentAbort = () => controller.abort();
      signal.addEventListener("abort", onParentAbort, { once: true });
      this.dataset.hedronTypeahead = "pending";
      const url = source.includes("?")
        ? `${source}&q=${encodeURIComponent(input.value)}`
        : `${source}?q=${encodeURIComponent(input.value)}`;
      fetch(url, { signal: controller.signal, headers: { Accept: "application/json" } })
        .then((res) => (res.ok ? res.json() : Promise.reject(new Error("typeahead"))))
        .then((body) => {
          if (requestId !== seq || revision !== this._revision) return;
          this.dataset.hedronTypeahead = "ready";
          this.dataset.hedronTypeaheadCount = String(
            Array.isArray(body) ? body.length : 0,
          );
        })
        .catch((err) => {
          if (controller.signal.aborted) return;
          this.dataset.hedronTypeahead = "error";
          this.setAttribute("data-hedron-optional-failure", err && err.message ? "1" : "1");
        });
    };
    input.addEventListener("input", onInput);
    this._cleanups.push(() => input.removeEventListener("input", onInput));
  }

  _disconnect() {
    if (this._ac) this._ac.abort();
    this._ac = null;
    for (const url of this._objectUrls) {
      try {
        URL.revokeObjectURL(url);
      } catch {
        /* ignore */
      }
    }
    this._objectUrls = [];
    for (const fn of this._cleanups) {
      try {
        fn();
      } catch {
        /* ignore */
      }
    }
    this._cleanups = [];
    this.dataset.hedronLifecycle = "disconnect";
  }
}

for (const tag of SUPPORTED_TAGS) {
  if (!customElements.get(tag)) {
    customElements.define(tag, class extends HedronExtrasHost {});
  }
}

function reconnectRoot(root) {
  if (!root || !root.querySelectorAll) return;
  for (const tag of SUPPORTED_TAGS) {
    if (root.matches && root.matches(tag) && typeof root._connect === "function") {
      root._connect("reconnect");
    }
    root.querySelectorAll(tag).forEach((el) => {
      if (typeof el._connect === "function") el._connect("reconnect");
    });
  }
}

document.addEventListener("htmx:afterSwap", (ev) => {
  reconnectRoot(ev.target);
});
document.addEventListener("htmx:oobAfterSwap", (ev) => {
  const target = (ev.detail && ev.detail.elt) || ev.target;
  reconnectRoot(target);
});

export { HedronExtrasHost, SUPPORTED_TAGS };
