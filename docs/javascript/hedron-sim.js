(function () {
  "use strict";

  var UTC_TOKEN = "__HEDRON_SIM_UTC__";
  var LOCAL_TOKEN = "__HEDRON_SIM_LOCAL_TIME__";

  function reducedMotion() {
    return (
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }

  function delayMs(normal) {
    return reducedMotion() ? Math.min(40, normal) : normal;
  }

  function utcStamp() {
    var now = new Date();
    var hh = String(now.getUTCHours()).padStart(2, "0");
    var mm = String(now.getUTCMinutes()).padStart(2, "0");
    var ss = String(now.getUTCSeconds()).padStart(2, "0");
    return hh + ":" + mm + ":" + ss + " UTC";
  }

  function localStamp() {
    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  function applyTokens(html) {
    return String(html || "")
      .split(UTC_TOKEN)
      .join(utcStamp())
      .split(LOCAL_TOKEN)
      .join(localStamp());
  }

  function parseRoutes(root) {
    var node = root.querySelector("[data-hedron-sim-routes]");
    if (!node) return null;
    try {
      return JSON.parse(node.textContent || "{}");
    } catch (err) {
      console.warn("hedron-sim: invalid route table", err);
      return null;
    }
  }

  function setTrace(root, text, isDeny) {
    var trace = root.querySelector("[data-hedron-sim-trace]");
    if (!trace) return;
    trace.hidden = false;
    trace.textContent = text;
    trace.classList.toggle("is-deny", Boolean(isDeny));
    trace.classList.add("is-visible");
  }

  function hxMethod(el) {
    if (el.hasAttribute("hx-get")) return "GET";
    if (el.hasAttribute("hx-post")) return "POST";
    if (el.hasAttribute("hx-put")) return "PUT";
    if (el.hasAttribute("hx-patch")) return "PATCH";
    if (el.hasAttribute("hx-delete")) return "DELETE";
    if (el.tagName === "FORM") return (el.getAttribute("method") || "POST").toUpperCase();
    return null;
  }

  function hxPath(el, method) {
    var attr = "hx-" + String(method || "").toLowerCase();
    if (el.hasAttribute(attr)) return el.getAttribute(attr);
    if (el.tagName === "FORM") return el.getAttribute("action") || "/";
    return null;
  }

  function findControl(eventTarget, root) {
    var el = eventTarget && eventTarget.closest
      ? eventTarget.closest("[hx-get],[hx-post],[hx-put],[hx-patch],[hx-delete]")
      : null;
    if (el && root.contains(el)) return el;
    return null;
  }

  function regionAllows(route, targetSelector) {
    var regions = (route && route.regions) || [];
    if (!regions.length) return true;
    if (!targetSelector) return false;
    for (var i = 0; i < regions.length; i += 1) {
      if (regions[i].selector === targetSelector || "#" + regions[i].id === targetSelector) {
        return true;
      }
    }
    return false;
  }

  function resolveTarget(root, selector) {
    if (!selector) return null;
    try {
      return root.querySelector(selector);
    } catch (err) {
      return null;
    }
  }

  function performSwap(target, html, swap) {
    var strategy = (swap || "innerHTML").toLowerCase();
    if (strategy === "outerhtml") {
      var wrap = document.createElement("div");
      wrap.innerHTML = html.trim();
      var next = wrap.firstElementChild;
      if (!next || !target.parentNode) {
        target.outerHTML = html;
        return target;
      }
      target.replaceWith(next);
      if (!reducedMotion()) {
        next.classList.add("hedron-sim--swapping");
        window.setTimeout(function () {
          next.classList.remove("hedron-sim--swapping");
        }, 450);
      }
      return next;
    }
    target.innerHTML = html;
    return target;
  }

  function applyOob(root, container) {
    var nodes = container.querySelectorAll("[hx-swap-oob]");
    for (var i = 0; i < nodes.length; i += 1) {
      var node = nodes[i];
      var id = node.id;
      if (!id) continue;
      var existing = root.querySelector("#" + CSS.escape(id));
      if (existing) existing.replaceWith(node);
      else node.remove();
    }
  }

  function splitPrimaryAndOob(html) {
    var wrap = document.createElement("div");
    wrap.innerHTML = html;
    var oob = wrap.querySelectorAll("[hx-swap-oob]");
    for (var i = 0; i < oob.length; i += 1) {
      oob[i].remove();
    }
    return { primary: wrap.innerHTML, full: html, container: wrap };
  }

  function handleRequest(root, table, control) {
    var method = hxMethod(control);
    var path = hxPath(control, method);
    if (!method || !path) return;

    var targetSel = control.getAttribute("hx-target");
    var swap = control.getAttribute("hx-swap") || "innerHTML";
    var key = method + " " + path;
    var route = table.routes && table.routes[key];

    control.setAttribute("aria-busy", "true");
    if ("disabled" in control) control.disabled = true;
    setTrace(root, method + " " + path + " → pending");

    window.setTimeout(function () {
      control.removeAttribute("aria-busy");
      if ("disabled" in control) control.disabled = false;

      if (!route) {
        setTrace(root, method + " " + path + " → 404 no simulated route", true);
        return;
      }

      if (!regionAllows(route, targetSel)) {
        setTrace(
          root,
          method + " " + path + " → 403 HX-Target not allowlisted",
          true
        );
        return;
      }

      var target = resolveTarget(root, targetSel) || control;
      var html = applyTokens(route.html || "");
      var parts = splitPrimaryAndOob(html);
      // Re-parse after token replace for OOB application on the live tree.
      var liveWrap = document.createElement("div");
      liveWrap.innerHTML = html;
      applyOob(root, liveWrap);
      var primaryWrap = document.createElement("div");
      primaryWrap.innerHTML = html;
      var oobNodes = primaryWrap.querySelectorAll("[hx-swap-oob]");
      for (var i = 0; i < oobNodes.length; i += 1) oobNodes[i].remove();
      performSwap(target, primaryWrap.innerHTML.trim() ? primaryWrap.innerHTML : parts.primary, swap);

      var status = route.status || 200;
      setTrace(root, method + " " + path + " → " + status + " fragment");
      try {
        control.focus({ preventScroll: true });
      } catch (err) {
        /* ignore */
      }
    }, delayMs(280));
  }

  function initRoot(root) {
    if (root.dataset.hedronSimReady === "true") return;
    root.dataset.hedronSimReady = "true";
    var table = parseRoutes(root);
    if (!table) return;

    // Seed any UTC tokens already present in the initial stage.
    var stage = root.querySelector("[data-hedron-sim-stage]") || root;
    stage.innerHTML = applyTokens(stage.innerHTML);

    root.addEventListener("click", function (event) {
      var control = findControl(event.target, root);
      if (!control) return;
      if (control.tagName === "A" || control.tagName === "BUTTON") {
        event.preventDefault();
        handleRequest(root, table, control);
      }
    });

    root.addEventListener("submit", function (event) {
      var form = event.target;
      if (!form || !root.contains(form)) return;
      if (!form.hasAttribute("hx-post") && !form.hasAttribute("hx-get")) return;
      event.preventDefault();
      handleRequest(root, table, form);
    });
  }

  function boot(doc) {
    var roots = doc.querySelectorAll("[data-hedron-sim]");
    for (var i = 0; i < roots.length; i += 1) initRoot(roots[i]);
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      boot(document);
    });
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      boot(document);
    });
  } else {
    boot(document);
  }

  window.HedronSim = {
    boot: boot,
    applyTokens: applyTokens,
  };
})();
