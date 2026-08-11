/**
 * ECharts host — expects window.echarts from local echarts.min.js.
 */
(function () {
  function fail(el, message) {
    el.setAttribute("data-hedron-chart-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) el.textContent = message;
  }
  function destroy(el) {
    try {
      if (window.echarts && typeof window.echarts.getInstanceByDom === "function") {
        var existing = window.echarts.getInstanceByDom(el);
        if (existing && typeof existing.dispose === "function") {
          existing.dispose();
        }
      }
    } catch (_) {
      /* ignore dispose errors during swap */
    }
    el.removeAttribute("data-hedron-chart-mounted");
  }
  function mount(el) {
    if (!window.echarts) {
      fail(el, "ECharts runtime missing (serve local echarts.min.js)");
      return;
    }
    destroy(el);
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
    el.setAttribute("data-hedron-chart-mounted", "1");
  }
  function scan(root) {
    (root || document).querySelectorAll('[data-hedron-chart="echarts"]').forEach(mount);
  }
  function beforeSwap(ev) {
    var target = ev && ev.target;
    if (!target || !target.querySelectorAll) return;
    target.querySelectorAll('[data-hedron-chart="echarts"]').forEach(destroy);
  }
  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.addEventListener("htmx:afterSwap", function (ev) {
    scan(ev.target);
  });
  document.addEventListener("htmx:beforeSwap", beforeSwap);
})();
