(function () {
  "use strict";

  var UTC_TOKEN = "__HEDRON_SIM_UTC__";
  var LOCAL_TOKEN = "__HEDRON_SIM_LOCAL_TIME__";
  var FORM_TOKEN_RE = /__HEDRON_SIM_FORM:([A-Za-z0-9_-]+)__/g;
  var LIST_INDEX_TOKEN = "__HEDRON_SIM_LIST_INDEX__";

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function listStore(root, selector) {
    if (!root._hedronSimLists) root._hedronSimLists = {};
    if (!root._hedronSimLists[selector]) root._hedronSimLists[selector] = [];
    return root._hedronSimLists[selector];
  }

  function findAccumulateRoute(table) {
    var routes = (table && table.routes) || {};
    var keys = Object.keys(routes);
    for (var i = 0; i < keys.length; i += 1) {
      if (routes[keys[i]].accumulate) return routes[keys[i]];
    }
    return null;
  }

  function renderAccumulatedList(root, targetSel, accumulate, items) {
    var regionId = String(targetSel || "").replace(/^#/, "");
    if (!items.length) {
      return accumulate.emptyHtml || '<div id="' + regionId + '"><p>No notes yet.</p></div>';
    }
    var field = accumulate.field || "note";
    var rows = "";
    for (var i = 0; i < items.length; i += 1) {
      (function (text, idx) {
        var fake = {
          get: function (name) {
            return name === field ? text : "";
          },
        };
        var row = applyTokens(accumulate.itemHtml || "", fake);
        row = row.split(LIST_INDEX_TOKEN).join(String(idx));
        rows += row;
      })(escapeHtml(items[i]), i);
    }
    // Item template is typically a bare <li>; wrap in the region container + ul.
    if (rows.indexOf("<li") === 0 || rows.indexOf("<LI") === 0) {
      return (
        '<div id="' +
        escapeHtml(regionId) +
        '"><ul class="hedron-sim-list">' +
        rows +
        "</ul></div>"
      );
    }
    return rows;
  }

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

  function applyTokens(html, formData) {
    var out = String(html || "")
      .split(UTC_TOKEN)
      .join(utcStamp())
      .split(LOCAL_TOKEN)
      .join(localStamp());
    // MkDocs historically mangled __token__ into <strong>token</strong>; accept both.
    out = out
      .split("<strong>HEDRON_SIM_UTC</strong>")
      .join(utcStamp())
      .split("<strong>HEDRON_SIM_LOCAL_TIME</strong>")
      .join(localStamp());
    return out.replace(FORM_TOKEN_RE, function (_match, name) {
      if (!formData) return "";
      var value = formData.get(name);
      return value == null ? "" : escapeHtml(String(value));
    });
  }

  function parseRoutes(root) {
    var node = root.querySelector("[data-hedron-sim-routes]");
    if (!node) return null;
    try {
      // <template> stores children in `.content` (textContent on the host can be empty).
      // Legacy <script type="application/json"> uses host textContent.
      var raw = "";
      if (node.content) {
        raw = node.content.textContent || "";
      }
      if (!String(raw).trim()) {
        raw = node.textContent || "";
      }
      if (!String(raw).trim()) return null;
      return JSON.parse(raw);
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
    var el =
      eventTarget && eventTarget.closest
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
      var selector = regions[i].selector;
      var idSel = "#" + regions[i].id;
      if (selector === targetSelector || idSel === targetSelector) {
        return true;
      }
      // Lazy inner wrapper: declared #id, hx-target #id-body
      if (targetSelector === selector + "-body" || targetSelector === idSel + "-body") {
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

  function emailValid(value) {
    var email = String(value || "").trim();
    return email.length >= 3 && email.indexOf("@") !== -1;
  }

  function nextSequenceIndex(root, key, length) {
    if (!root._hedronSimSeq) root._hedronSimSeq = {};
    var index = root._hedronSimSeq[key] || 0;
    var stepIndex = index % length;
    root._hedronSimSeq[key] = index + 1;
    return stepIndex;
  }

  function credentialsValid(formData) {
    var user = formData ? String(formData.get("username") || "") : "";
    var pass = formData ? String(formData.get("password") || "") : "";
    return user === "ada" && pass === "correct-horse";
  }

  function resolveRoutePayload(root, route, key, formData) {
    if (route.validate === "email" && route.variants) {
      var email = formData ? formData.get("email") : "";
      var variantKey = emailValid(email) ? "valid" : "invalid";
      return route.variants[variantKey] || route;
    }
    if (route.validate === "credentials" && route.variants) {
      var credKey = credentialsValid(formData) ? "valid" : "invalid";
      return route.variants[credKey] || route;
    }
    if (route.sequence && route.sequence.length) {
      var idx = nextSequenceIndex(root, key, route.sequence.length);
      return route.sequence[idx] || route;
    }
    return route;
  }

  function performSwap(target, html, swap) {
    var strategy = (swap || "innerHTML").toLowerCase();
    if (strategy === "delete" || strategy === "outerhtml delete") {
      target.remove();
      return null;
    }
    if (strategy === "none") return target;
    if (strategy === "beforeend") {
      target.insertAdjacentHTML("beforeend", html);
      return target;
    }
    if (strategy === "afterbegin") {
      target.insertAdjacentHTML("afterbegin", html);
      return target;
    }
    if (strategy === "beforebegin") {
      target.insertAdjacentHTML("beforebegin", html);
      return target;
    }
    if (strategy === "afterend") {
      target.insertAdjacentHTML("afterend", html);
      return target;
    }
    if (strategy === "outerhtml") {
      var wrap = document.createElement("div");
      wrap.innerHTML = html.trim();
      var parent = target.parentNode;
      if (!parent) {
        target.outerHTML = html;
        return target;
      }
      var frag = document.createDocumentFragment();
      var next = null;
      while (wrap.firstChild) {
        if (!next && wrap.firstChild.nodeType === 1) next = wrap.firstChild;
        frag.appendChild(wrap.firstChild);
      }
      parent.replaceChild(frag, target);
      if (next && !reducedMotion()) {
        next.classList.add("hedron-sim--swapping");
        window.setTimeout(function () {
          next.classList.remove("hedron-sim--swapping");
        }, 450);
      }
      return next || target;
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
      node.removeAttribute("hx-swap-oob");
      var existing = root.querySelector("#" + CSS.escape(id));
      if (existing) existing.replaceWith(node);
      else node.remove();
    }
  }

  function applyEffects(root, effects) {
    var handledPrimary = false;
    var items = Array.isArray(effects) ? effects : [];
    for (var i = 0; i < items.length; i += 1) {
      var effect = items[i] || {};
      var target = resolveTarget(root, effect.target);
      if (effect.type === "refresh" && target) {
        performSwap(target, applyTokens(effect.html || "", null), "outerHTML");
        handledPrimary = true;
      }
    }
    return handledPrimary;
  }

  function handleRequest(root, table, control, formData) {
    var method = hxMethod(control);
    var path = hxPath(control, method);
    if (!method || !path) return;

    var confirmMsg =
      control.getAttribute("hx-confirm") || control.getAttribute("data-confirm");
    if (confirmMsg && !window.confirm(confirmMsg)) {
      setTrace(root, method + " " + path + " → cancelled");
      return;
    }

    var targetSel = control.getAttribute("hx-target");
    // Edron page navigation intentionally leaves the target implicit in the
    // source API. A static app preview has one bounded stage, so page links
    // replace that stage rather than the clicked link itself.
    if (!targetSel && control.matches && control.matches("[data-hedron-nav-link]")) {
      targetSel = "[data-hedron-sim-stage]";
    }
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
        setTrace(root, method + " " + path + " → 403 HX-Target not allowlisted", true);
        return;
      }

      var target = resolveTarget(root, targetSel) || control;
      var html;
      var status = route.status || 200;
      var handledPrimary = false;

      if (route.accumulate) {
        var store = listStore(root, targetSel || route.accumulate.field);
        var field = route.accumulate.field || "note";
        var value = formData ? String(formData.get(field) || "").trim() : "";
        if (value) store.push(value);
        html = renderAccumulatedList(root, targetSel, route.accumulate, store);
      } else if (route.listRemove) {
        var accRoute = findAccumulateRoute(table);
        var list = listStore(root, targetSel || "#notes-list");
        var idxAttr = control.getAttribute("data-hedron-sim-list-index");
        var idx = idxAttr == null ? list.length - 1 : Number(idxAttr);
        if (!Number.isNaN(idx) && idx >= 0 && idx < list.length) list.splice(idx, 1);
        if (accRoute && accRoute.accumulate) {
          html = renderAccumulatedList(root, targetSel, accRoute.accumulate, list);
        } else {
          html = applyTokens(route.html || "", formData);
        }
      } else {
        var payload = resolveRoutePayload(root, route, key, formData);
        status = payload.status || route.status || 200;
        html = applyTokens(payload.html || "", formData);
        handledPrimary = applyEffects(root, payload.effects, formData);
        var liveWrap = document.createElement("div");
        liveWrap.innerHTML = html;
        applyOob(root, liveWrap);
        var primaryWrap = document.createElement("div");
        primaryWrap.innerHTML = html;
        var oobNodes = primaryWrap.querySelectorAll("[hx-swap-oob]");
        for (var i = 0; i < oobNodes.length; i += 1) oobNodes[i].remove();
        html = primaryWrap.innerHTML;
      }

      if (!handledPrimary) performSwap(target, html, swap);

      var label = status >= 400 ? true : false;
      setTrace(root, method + " " + path + " → " + status + " fragment", label);
      try {
        control.focus({ preventScroll: true });
      } catch (err) {
        /* ignore */
      }
    }, delayMs(280));
  }

  function recordBlocked(root, reason) {
    var prev = root.dataset.hedronSimBlocked || "";
    var next = prev ? prev + "|" + reason : reason;
    root.dataset.hedronSimBlocked = next;
  }

  var _guardingRoot = null;
  var _guardClearTimer = null;

  function beginSimGuard(root) {
    _guardingRoot = root;
    if (_guardClearTimer) window.clearTimeout(_guardClearTimer);
    _guardClearTimer = window.setTimeout(function () {
      _guardingRoot = null;
      _guardClearTimer = null;
    }, 800);
  }

  function neutralizeProgressiveAnchors(root) {
    // Docs sims keep real hx-* behavior, but absolute/root hrefs like "/reports"
    // are same-origin on Read the Docs. Material instant navigation (or no-JS
    // progressive enhancement) follows them and can trip Cloudflare WAF.
    var anchors = root.querySelectorAll("a[href]");
    for (var i = 0; i < anchors.length; i += 1) {
      var anchor = anchors[i];
      var href = anchor.getAttribute("href");
      if (!href || href === "#" || href.charAt(0) === "#" || href.indexOf("javascript:") === 0) {
        continue;
      }
      if (!anchor.hasAttribute("data-hedron-sim-href")) {
        anchor.setAttribute("data-hedron-sim-href", href);
      }
      anchor.setAttribute("href", "#");
    }
    // Neutralize every form — missing action still POSTs the current docs URL
    // on Read the Docs and trips Cloudflare WAF.
    var forms = root.querySelectorAll("form");
    for (var f = 0; f < forms.length; f += 1) {
      var form = forms[f];
      var action = form.getAttribute("action");
      if (action && action !== "#" && action.charAt(0) !== "#") {
        if (!form.hasAttribute("data-hedron-sim-action")) {
          form.setAttribute("data-hedron-sim-action", action);
        }
      }
      form.setAttribute("action", "#");
    }
  }

  function enforceBootInvariants(root) {
    // Repair anything that slipped past neutralize (or was injected later).
    var badAnchors = root.querySelectorAll('a[href^="/"], a[href^="http"]');
    for (var i = 0; i < badAnchors.length; i += 1) {
      var anchor = badAnchors[i];
      if (!anchor.hasAttribute("data-hedron-sim-href")) {
        anchor.setAttribute("data-hedron-sim-href", anchor.getAttribute("href") || "");
      }
      anchor.setAttribute("href", "#");
      recordBlocked(root, "href");
    }
    var forms = root.querySelectorAll("form");
    for (var f = 0; f < forms.length; f += 1) {
      var form = forms[f];
      var action = form.getAttribute("action");
      if (action !== "#") {
        if (action && action !== "#" && !form.hasAttribute("data-hedron-sim-action")) {
          form.setAttribute("data-hedron-sim-action", action);
        }
        form.setAttribute("action", "#");
        recordBlocked(root, "form-action");
      }
    }
  }

  function installNetworkTripwire() {
    // Only active while a sim click/submit is being handled — never blocks
    // MkDocs / Read the Docs analytics outside that window.
    if (window._hedronSimFetchPatched) return;
    window._hedronSimFetchPatched = true;
    if (typeof window.fetch === "function") {
      var nativeFetch = window.fetch.bind(window);
      window.fetch = function (input, init) {
        if (_guardingRoot) {
          recordBlocked(_guardingRoot, "fetch");
          return Promise.reject(new Error("hedron-sim: blocked network fetch"));
        }
        return nativeFetch(input, init);
      };
    }
    if (typeof window.XMLHttpRequest === "function") {
      var NativeXHR = window.XMLHttpRequest;
      window.XMLHttpRequest = function () {
        var xhr = new NativeXHR();
        var nativeOpen = xhr.open;
        xhr.open = function () {
          if (_guardingRoot) {
            recordBlocked(_guardingRoot, "xhr");
            throw new Error("hedron-sim: blocked XMLHttpRequest");
          }
          return nativeOpen.apply(xhr, arguments);
        };
        return xhr;
      };
    }
  }

  function initRoot(root) {
    if (root.dataset.hedronSimReady === "true") return;
    var table = parseRoutes(root);
    if (!table) return;
    root.dataset.hedronSimReady = "true";
    root._hedronSimTable = table;

    var stage = root.querySelector("[data-hedron-sim-stage]") || root;
    stage.innerHTML = applyTokens(stage.innerHTML, null);
    neutralizeProgressiveAnchors(root);
    enforceBootInvariants(root);
    installNetworkTripwire();

    // Bounded auto-poll for hx-trigger="every Nms" (docs demos only).
    var polls = root.querySelectorAll("[hx-trigger]");
    for (var p = 0; p < polls.length; p += 1) {
      var el = polls[p];
      var trigger = el.getAttribute("hx-trigger") || "";
      var match = /every\s+(\d+)\s*ms/i.exec(trigger);
      if (!match) continue;
      (function (control, ms) {
        var ticks = 0;
        var timer = window.setInterval(function () {
          ticks += 1;
          handleRequest(root, table, control, null);
          if (ticks >= 4) window.clearInterval(timer);
        }, Math.max(delayMs(Number(ms) || 700), 400));
      })(el, match[1]);
    }

    // One-shot load trigger (Lazy and similar).
    var loads = root.querySelectorAll('[hx-trigger="load"]');
    for (var l = 0; l < loads.length; l += 1) {
      (function (control) {
        window.setTimeout(function () {
          handleRequest(root, table, control, null);
        }, delayMs(120));
      })(loads[l]);
    }
  }

  function ensureRoot(root) {
    if (!root) return null;
    if (root.dataset.hedronSimReady !== "true") initRoot(root);
    return root.dataset.hedronSimReady === "true" ? root : null;
  }

  function initModeDemo(root) {
    if (root.dataset.hedronSimReady === "true") return;
    root.dataset.hedronSimReady = "true";
    var toggles = root.querySelectorAll("[data-sim-mode]");
    var panes = root.querySelectorAll("[data-sim-mode-pane]");
    var status = root.querySelector("[data-sim-mode-status]");
    function select(mode) {
      for (var i = 0; i < toggles.length; i += 1) {
        var active = toggles[i].getAttribute("data-sim-mode") === mode;
        toggles[i].setAttribute("aria-pressed", String(active));
        toggles[i].classList.toggle("hedron-sim-btn--primary", active);
      }
      for (var j = 0; j < panes.length; j += 1) {
        panes[j].hidden = panes[j].getAttribute("data-sim-mode-pane") !== mode;
      }
      if (status) {
        status.textContent =
          mode === "page" ? "PAGE: full HTML document." : "FRAGMENT: region HTML only.";
      }
    }
    for (var t = 0; t < toggles.length; t += 1) {
      toggles[t].addEventListener("click", function (event) {
        event.preventDefault();
        select(event.currentTarget.getAttribute("data-sim-mode"));
      });
    }
  }

  function boot(doc) {
    var roots = doc.querySelectorAll("[data-hedron-sim]");
    for (var i = 0; i < roots.length; i += 1) initRoot(roots[i]);
    var modes = doc.querySelectorAll("[data-hedron-sim-modes]");
    for (var m = 0; m < modes.length; m += 1) initModeDemo(modes[m]);
  }

  // Capture-phase handlers beat MkDocs Material instant-navigation, which otherwise
  // follows demo <a href="/…"> paths and leaves the docs page.
  document.addEventListener(
    "click",
    function (event) {
      var target = event.target;
      // Clicks on button label text can target a Text node (no .closest).
      if (target && target.nodeType === 3) target = target.parentElement;
      if (!target || !target.closest) return;
      var root = target.closest("[data-hedron-sim]");
      if (!root || !ensureRoot(root)) return;
      beginSimGuard(root);
      var control = findControl(target, root);
      // Submit controls inherit hx-* from the enclosing form — treat as form submit.
      if (control && control.tagName === "FORM") {
        var submitter = target.closest("button, input[type='submit']");
        if (submitter && control.contains(submitter)) {
          event.preventDefault();
          event.stopPropagation();
          if (typeof event.stopImmediatePropagation === "function") {
            event.stopImmediatePropagation();
          }
          handleRequest(root, root._hedronSimTable, control, new FormData(control));
          return;
        }
      } else if (control) {
        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === "function") {
          event.stopImmediatePropagation();
        }
        handleRequest(root, root._hedronSimTable, control, null);
        return;
      }
      // Block progressive-enhancement navigation even when hx-* is absent.
      var anchor = target.closest("a[href]");
      if (anchor && root.contains(anchor)) {
        var href = anchor.getAttribute("href") || "";
        if (href && href !== "#" && href.charAt(0) !== "#") {
          event.preventDefault();
          event.stopPropagation();
          if (typeof event.stopImmediatePropagation === "function") {
            event.stopImmediatePropagation();
          }
          recordBlocked(root, "nav");
        }
      }
    },
    true
  );

  document.addEventListener(
    "submit",
    function (event) {
      var form = event.target;
      if (!form || !form.closest) return;
      var root = form.closest("[data-hedron-sim]");
      if (!root) return;
      // Always cancel native submit first — a real POST to the docs host is blocked
      // by Cloudflare and looks like a broken demo.
      event.preventDefault();
      event.stopPropagation();
      if (typeof event.stopImmediatePropagation === "function") {
        event.stopImmediatePropagation();
      }
      beginSimGuard(root);
      if (!ensureRoot(root)) {
        recordBlocked(root, "submit");
        return;
      }
      if (!form.hasAttribute("hx-post") && !form.hasAttribute("hx-get")) return;
      handleRequest(root, root._hedronSimTable, form, new FormData(form));
    },
    true
  );

  // Boot on first paint and again whenever Material swaps page content
  // (navigation.instant). document$ may or may not emit synchronously on subscribe.
  function scheduleBoot() {
    boot(document);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleBoot);
  } else {
    scheduleBoot();
  }
  if (typeof document$ !== "undefined") {
    document$.subscribe(scheduleBoot);
  }

  window.HedronSim = {
    boot: boot,
    applyTokens: applyTokens,
    beginSimGuard: beginSimGuard,
  };
})();
