/**
 * Chart.js host — expects window.Chart from local chart.umd.min.js.
 * Spec arrives as non-executable JSON via data-hedron-payload.
 */
(function () {
  function fail(el, message) {
    el.setAttribute("data-hedron-chart-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) el.textContent = message;
  }
  function destroy(el) {
    try {
      var canvas = el.querySelector("canvas");
      var chart =
        canvas && window.Chart && typeof window.Chart.getChart === "function"
          ? window.Chart.getChart(canvas)
          : null;
      if (chart && typeof chart.destroy === "function") {
        chart.destroy();
      }
    } catch (_) {
      /* ignore destroy errors during swap */
    }
    el.removeAttribute("data-hedron-chart-mounted");
  }
  function mount(el) {
    if (!window.Chart) {
      fail(el, "Chart.js runtime missing (serve local chart.umd.min.js)");
      return;
    }
    destroy(el);
    var raw = el.getAttribute("data-hedron-payload");
    if (!raw) return;
    var payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      fail(el, "Invalid Chart.js payload JSON");
      return;
    }
    var spec = payload.spec || payload;
    var canvas = document.createElement("canvas");
    el.innerHTML = "";
    el.appendChild(canvas);
    new window.Chart(canvas.getContext("2d"), spec);
    el.setAttribute("data-hedron-chart-mounted", "1");
  }
  function scan(root) {
    var base = root || document;
    var sel = '[data-hedron-chart="chartjs"]';
    if (base.matches && base.matches(sel)) mount(base);
    if (base.querySelectorAll) base.querySelectorAll(sel).forEach(mount);
  }
  function beforeSwap(ev) {
    var target = ev && ev.target;
    if (!target) return;
    var sel = '[data-hedron-chart="chartjs"]';
    if (target.matches && target.matches(sel)) destroy(target);
    if (target.querySelectorAll) target.querySelectorAll(sel).forEach(destroy);
  }
  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.addEventListener("htmx:afterSwap", function (ev) {
    scan(ev.target);
  });
  document.addEventListener("htmx:beforeSwap", beforeSwap);
})();
