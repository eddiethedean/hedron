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
  function mount(el) {
    if (!window.Chart) {
      fail(el, "Chart.js runtime missing (serve local chart.umd.min.js)");
      return;
    }
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
  }
  function scan(root) {
    (root || document).querySelectorAll('[data-hedron-chart="chartjs"]').forEach(mount);
  }
  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.body &&
    document.body.addEventListener("htmx:afterSwap", function (ev) {
      scan(ev.target);
    });
})();
