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

  function destroy(el) {
    try {
      if (el && el._vegaView && typeof el._vegaView.finalize === "function") {
        el._vegaView.finalize();
      }
    } catch (_) {
      /* ignore */
    }
    el._vegaView = null;
    el.removeAttribute("data-hedron-chart-mounted");
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
    const result = window.vegaEmbed(el, payload.spec || payload, { actions: false });
    el.setAttribute("data-hedron-chart-mounted", "1");
    if (result && typeof result.then === "function") {
      result.then(function (res) {
        if (res && res.view) {
          el._vegaView = res.view;
        }
      });
    }
  }

  function scan(root) {
    (root || document)
      .querySelectorAll('[data-hedron-chart="vega-lite"]')
      .forEach(mount);
  }

  function beforeSwap(ev) {
    const target = ev && ev.target;
    if (!target || !target.querySelectorAll) return;
    target.querySelectorAll('[data-hedron-chart="vega-lite"]').forEach(destroy);
  }

  document.addEventListener("DOMContentLoaded", () => scan(document));
  document.body &&
    document.body.addEventListener("htmx:afterSwap", (ev) => {
      scan(ev.target);
    });
  document.body && document.body.addEventListener("htmx:beforeSwap", beforeSwap);
})();
