/**
 * Mermaid host — expects window.mermaid from local mermaid.min.js.
 */
(function () {
  var initialized = false;
  function fail(el, message) {
    el.setAttribute("data-hedron-chart-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) el.textContent = message;
  }
  function destroy(el) {
    el.innerHTML = "";
    el.removeAttribute("data-hedron-chart-mounted");
  }
  function mount(el) {
    if (!window.mermaid) {
      fail(el, "Mermaid runtime missing (serve local mermaid.min.js)");
      return;
    }
    destroy(el);
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
    var pre = document.createElement("pre");
    pre.className = "mermaid";
    pre.textContent = diagram;
    el.appendChild(pre);
    if (!initialized) {
      window.mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
      initialized = true;
    }
    window.mermaid.run({ nodes: [pre] });
    el.setAttribute("data-hedron-chart-mounted", "1");
  }
  function scan(root) {
    var base = root || document;
    var sel = '[data-hedron-chart="mermaid"]';
    if (base.matches && base.matches(sel)) mount(base);
    if (base.querySelectorAll) base.querySelectorAll(sel).forEach(mount);
  }
  function beforeSwap(ev) {
    var target = ev && ev.target;
    if (!target) return;
    var sel = '[data-hedron-chart="mermaid"]';
    if (target.matches && target.matches(sel)) destroy(target);
    if (target.querySelectorAll) target.querySelectorAll(sel).forEach(destroy);
  }
  function oobTarget(ev) {
    return (ev && ev.detail && ev.detail.elt) || (ev && ev.target) || null;
  }
  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.addEventListener("htmx:afterSwap", function (ev) {
    scan(ev.target);
  });
  document.addEventListener("htmx:beforeSwap", beforeSwap);
  document.addEventListener("htmx:oobAfterSwap", function (ev) {
    scan(oobTarget(ev));
  });
  document.addEventListener("htmx:oobBeforeSwap", function (ev) {
    beforeSwap({ target: oobTarget(ev) });
  });
  document.addEventListener("htmx:load", function (ev) {
    scan(ev.target);
  });
})();
