/**
 * ECharts host — expects window.echarts from local echarts.min.js.
 */
(function () {
  function fail(el, message) {
    el.setAttribute("data-hedron-chart-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) el.textContent = message;
  }
  function mount(el) {
    if (!window.echarts) {
      fail(el, "ECharts runtime missing (serve local echarts.min.js)");
      return;
    }
    var raw = el.getAttribute("data-hedron-payload");
    if (!raw) return;
    var payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      fail(el, "Invalid ECharts payload JSON");
      return;
    }
    var chart = window.echarts.init(el);
    chart.setOption(payload.spec || payload);
  }
  function scan(root) {
    (root || document).querySelectorAll('[data-hedron-chart="echarts"]').forEach(mount);
  }
  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.body &&
    document.body.addEventListener("htmx:afterSwap", function (ev) {
      scan(ev.target);
    });
})();
