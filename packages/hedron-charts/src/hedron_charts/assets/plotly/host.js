/**
 * Hedron Plotly chart host — expects a locally served Plotly runtime on window.Plotly.
 * Specs arrive as non-executable JSON via data-hedron-payload.
 * Full Plotly runtime pinning is deferred/experimental; fail closed when missing.
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
    if (!window.Plotly) {
      fail(
        el,
        "Plotly runtime missing: serve a pinned local Plotly build or treat interactive Plotly as experimental."
      );
      return;
    }
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      fail(el, "Invalid Plotly chart payload JSON");
      return;
    }
    const spec = payload.spec || payload;
    window.Plotly.newPlot(el, spec.data || [], spec.layout || {}, {
      displayModeBar: false,
      responsive: true,
      staticPlot: false,
    });
  }

  function scan(root) {
    (root || document)
      .querySelectorAll('[data-hedron-chart="plotly"]')
      .forEach(mount);
  }

  document.addEventListener("DOMContentLoaded", () => scan(document));
  document.body &&
    document.body.addEventListener("htmx:afterSwap", (ev) => {
      scan(ev.target);
    });
})();
