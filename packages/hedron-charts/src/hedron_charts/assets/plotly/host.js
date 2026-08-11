/**
 * Hedron Plotly chart host — expects a locally served Plotly runtime on window.Plotly.
 * Specs arrive as non-executable JSON via data-hedron-payload.
 * Typed chart events dispatch as CustomEvents for HTMX/action bridges.
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

  function emit(el, name, detail) {
    el.dispatchEvent(
      new CustomEvent(name, {
        bubbles: true,
        composed: true,
        detail: detail || {},
      })
    );
  }

  function bindEvents(el) {
    if (!window.Plotly || !el.on) {
      // Plotly.newPlot returns a promise; attach via gd once ready.
    }
    const gd = el;
    gd.on &&
      gd.on("plotly_click", function (data) {
        const pt = (data.points && data.points[0]) || {};
        emit(el, "hedron-chart-click", {
          kind: "click",
          trace_id: String(pt.curveNumber != null ? pt.curveNumber : "0"),
          point_index: pt.pointIndex != null ? pt.pointIndex : null,
          payload: { x: pt.x, y: pt.y },
          accessible_fallback: "Selected chart point",
        });
      });
    gd.on &&
      gd.on("plotly_hover", function (data) {
        const pt = (data.points && data.points[0]) || {};
        emit(el, "hedron-chart-hover", {
          kind: "hover",
          trace_id: String(pt.curveNumber != null ? pt.curveNumber : "0"),
          point_index: pt.pointIndex != null ? pt.pointIndex : null,
          payload: { x: pt.x, y: pt.y },
        });
      });
    gd.on &&
      gd.on("plotly_selected", function (data) {
        emit(el, "hedron-chart-select", {
          kind: data && data.range ? "box" : "lasso",
          trace_id: "selection",
          payload: { count: (data && data.points && data.points.length) || 0 },
        });
      });
    gd.on &&
      gd.on("plotly_relayout", function (eventData) {
        emit(el, "hedron-chart-relayout", {
          kind: "relayout",
          trace_id: "layout",
          payload: eventData || {},
        });
      });
    gd.on &&
      gd.on("plotly_restyle", function (eventData) {
        emit(el, "hedron-chart-restyle", {
          kind: "restyle",
          trace_id: "style",
          payload: eventData || {},
        });
      });
  }

  function destroy(el) {
    try {
      if (window.Plotly && typeof window.Plotly.purge === "function") {
        window.Plotly.purge(el);
      }
    } catch (_) {
      /* ignore purge errors during swap */
    }
    el.removeAttribute("data-hedron-chart-mounted");
  }

  function mount(el) {
    const raw = el.getAttribute("data-hedron-payload");
    if (!raw) return;
    if (!window.Plotly) {
      fail(
        el,
        "Plotly runtime missing: serve a pinned local Plotly build (hedron-charts pins)."
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
    const plotted = window.Plotly.newPlot(el, spec.data || [], spec.layout || {}, {
      displayModeBar: false,
      responsive: true,
      staticPlot: false,
    });
    el.setAttribute("data-hedron-chart-mounted", "1");
    if (plotted && typeof plotted.then === "function") {
      plotted.then(function () {
        bindEvents(el);
      });
    } else {
      bindEvents(el);
    }
  }

  function scan(root) {
    (root || document)
      .querySelectorAll('[data-hedron-chart="plotly"]')
      .forEach(mount);
  }

  function beforeSwap(ev) {
    const target = ev && ev.target;
    if (!target || !target.querySelectorAll) return;
    target.querySelectorAll('[data-hedron-chart="plotly"]').forEach(destroy);
  }

  document.addEventListener("DOMContentLoaded", () => scan(document));
  document.body &&
    document.body.addEventListener("htmx:afterSwap", (ev) => {
      scan(ev.target);
    });
  document.body && document.body.addEventListener("htmx:beforeSwap", beforeSwap);
})();
