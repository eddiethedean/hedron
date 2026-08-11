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
    el._hedronVegaGen = (el._hedronVegaGen || 0) + 1;
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
    destroy(el);
    const gen = (el._hedronVegaGen || 0) + 1;
    el._hedronVegaGen = gen;
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
        if (el._hedronVegaGen !== gen) {
          try {
            if (res && res.view && typeof res.view.finalize === "function") {
              res.view.finalize();
            }
          } catch (_) {
            /* ignore stale finalize */
          }
          return;
        }
        if (res && res.view) {
          el._vegaView = res.view;
        }
      });
    }
  }

  function scan(root) {
    var base = root || document;
    var sel = '[data-hedron-chart="vega-lite"]';
    if (base.matches && base.matches(sel)) mount(base);
    if (base.querySelectorAll) base.querySelectorAll(sel).forEach(mount);
  }

  function beforeSwap(ev) {
    const target = ev && ev.target;
    if (!target) return;
    var sel = '[data-hedron-chart="vega-lite"]';
    if (target.matches && target.matches(sel)) destroy(target);
    if (target.querySelectorAll) target.querySelectorAll(sel).forEach(destroy);
  }

  function oobTarget(ev) {
    return (ev && ev.detail && ev.detail.elt) || (ev && ev.target) || null;
  }

  document.addEventListener("DOMContentLoaded", () => scan(document));
  document.addEventListener("htmx:afterSwap", (ev) => {
    scan(ev.target);
  });
  document.addEventListener("htmx:beforeSwap", beforeSwap);
  document.addEventListener("htmx:oobAfterSwap", (ev) => {
    scan(oobTarget(ev));
  });
  document.addEventListener("htmx:oobBeforeSwap", (ev) => {
    beforeSwap({ target: oobTarget(ev) });
  });
  document.addEventListener("htmx:load", (ev) => {
    scan(ev.target);
  });
})();
