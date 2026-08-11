/**
 * Lightweight static/fallback host for adapters that render JSON summaries
 * when interactive runtimes are optional (sigma/three/bokeh/holoviews/datashader).
 */
(function () {
  var SELECTOR =
    '[data-hedron-chart="static"],[data-hedron-chart="sigma"],[data-hedron-chart="threejs"],[data-hedron-chart="bokeh"],[data-hedron-chart="holoviews"]';
  function destroy(el) {
    el.innerHTML = "";
    el.removeAttribute("data-hedron-chart-mounted");
  }
  function mount(el) {
    destroy(el);
    var raw = el.getAttribute("data-hedron-payload");
    if (!raw) return;
    var payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      el.textContent = "Invalid chart payload";
      return;
    }
    var pre = document.createElement("pre");
    pre.textContent = JSON.stringify(payload.spec || payload, null, 2).slice(0, 4000);
    el.appendChild(pre);
    el.setAttribute("data-hedron-chart-mounted", "1");
  }
  function scan(root) {
    (root || document).querySelectorAll(SELECTOR).forEach(mount);
  }
  function beforeSwap(ev) {
    var target = ev && ev.target;
    if (!target || !target.querySelectorAll) return;
    target.querySelectorAll(SELECTOR).forEach(destroy);
  }
  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.addEventListener("htmx:afterSwap", function (ev) {
    scan(ev.target);
  });
  document.addEventListener("htmx:beforeSwap", beforeSwap);
})();
