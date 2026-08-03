/**
 * Hedron Vega-Lite chart host — expects window.vegaEmbed from a locally served runtime.
 * Specs arrive as non-executable JSON via data-hedron-payload.
 */
(function () {
  function mount(el) {
    const raw = el.getAttribute("data-hedron-payload");
    if (!raw || !window.vegaEmbed) return;
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
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
