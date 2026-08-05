/**
 * Lightweight static/fallback host for adapters that render JSON summaries
 * when interactive runtimes are optional (sigma/three/bokeh/holoviews/datashader).
 */
(function () {
  function mount(el) {
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
    el.innerHTML = "";
    el.appendChild(pre);
  }
  function scan(root) {
    (root || document)
      .querySelectorAll(
        '[data-hedron-chart="static"],[data-hedron-chart="sigma"],[data-hedron-chart="threejs"],[data-hedron-chart="bokeh"],[data-hedron-chart="holoviews"]'
      )
      .forEach(mount);
  }
  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.body &&
    document.body.addEventListener("htmx:afterSwap", function (ev) {
      scan(ev.target);
    });
})();
