/**
 * Hedron Vega-Lite chart host — expects window.vegaEmbed from a locally served runtime.
 * Specs arrive as non-executable JSON via data-hedron-payload.
 * Full Vega runtime pinning is deferred/experimental; fail closed when missing.
 */
(function () {
  function fail(el, message) {
    el.setAttribute("data-hedron-chart-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) {
      el.textContent = message;
    }
    if (typeof console !== "undefined" && console.error) {
      console.error("[hedron-charts]", message);
    }
  }

  function mount(el) {
    const raw = el.getAttribute("data-hedron-payload");
    if (!raw) return;
    if (!window.vegaEmbed) {
      fail(
        el,
        "Vega runtime missing: serve a pinned local vegaEmbed build or treat interactive Vega as experimental."
      );
      return;
    }
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      fail(el, "Invalid Vega-Lite chart payload JSON");
      return;
    }
    window.vegaEmbed(el, payload.spec || payload, { actions: false });
  }

  function scan(root) {
    (root || document)
      .querySelectorAll('[data-hedron-chart="vega-lite"]')
      .forEach(mount);
  }

  document.addEventListener("DOMContentLoaded", () => scan(document));
  document.body &&
    document.body.addEventListener("htmx:afterSwap", (ev) => {
      scan(ev.target);
    });
})();
