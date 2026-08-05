/**
 * Mermaid host — expects window.mermaid from local mermaid.min.js.
 */
(function () {
  function fail(el, message) {
    el.setAttribute("data-hedron-chart-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) el.textContent = message;
  }
  function mount(el) {
    if (!window.mermaid) {
      fail(el, "Mermaid runtime missing (serve local mermaid.min.js)");
      return;
    }
    var raw = el.getAttribute("data-hedron-payload");
    if (!raw) return;
    var payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      fail(el, "Invalid Mermaid payload JSON");
      return;
    }
    var spec = payload.spec || payload;
    var diagram = (spec && spec.diagram) || String(spec);
    el.innerHTML = "";
    var pre = document.createElement("pre");
    pre.className = "mermaid";
    pre.textContent = diagram;
    el.appendChild(pre);
    window.mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
    window.mermaid.run({ nodes: [pre] });
  }
  function scan(root) {
    (root || document).querySelectorAll('[data-hedron-chart="mermaid"]').forEach(mount);
  }
  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.body &&
    document.body.addEventListener("htmx:afterSwap", function (ev) {
      scan(ev.target);
    });
})();
