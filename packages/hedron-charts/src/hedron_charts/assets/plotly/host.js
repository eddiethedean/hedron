/**
 * Hedron Plotly chart host — expects a locally served Plotly runtime on window.Plotly.
 * Specs arrive as non-executable JSON via data-hedron-payload.
 */
(function () {
  function mount(el) {
    const raw = el.getAttribute("data-hedron-payload");
    if (!raw || !window.Plotly) return;
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
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
