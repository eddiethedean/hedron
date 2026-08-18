/**
 * hedron-map — first-party map element (phase 0.47 / RFC-0074).
 * Consumes a compiled MapPlan via data-hedron-payload only.
 * MapLibre symbols stay behind this host. Generation-guarded HTMX dispose.
 */
const TAG = "hedron-map";
const ABI = "1";
const bags = new WeakMap();

function bag(el) {
  let state = bags.get(el);
  if (!state) {
    state = { ac: new AbortController(), gen: 0, map: null, timer: 0, ro: null };
    bags.set(el, state);
  }
  return state;
}

function parsePlan(el) {
  const raw = el.getAttribute("data-hedron-payload");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (_) {
    return null;
  }
}

function cookieValue(name) {
  const parts = (document.cookie || "").split("; ");
  for (const part of parts) {
    if (part.startsWith(name + "=")) return decodeURIComponent(part.slice(name.length + 1));
  }
  return "";
}

function commandMap(el) {
  const raw = el.getAttribute("data-hedron-map-commands");
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (_) {
    return {};
  }
}

function postCommand(url, detail) {
  const token = cookieValue("hedron_csrf");
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json, text/html",
    "HX-Request": "true",
  };
  if (token) headers["X-CSRF-Token"] = token;
  const body = JSON.stringify(detail || {});
  if (window.htmx && typeof window.htmx.ajax === "function") {
    window.htmx.ajax("POST", url, {
      values: detail || {},
      headers: token ? { "X-CSRF-Token": token } : {},
      swap: "none",
    });
    return;
  }
  fetch(url, { method: "POST", credentials: "same-origin", headers, body });
}

function emit(el, kind, detail) {
  const payload = Object.assign({ kind }, detail || {});
  el.dispatchEvent(
    new CustomEvent("hedron-map-" + kind, {
      bubbles: true,
      composed: true,
      detail: payload,
    })
  );
  const url = commandMap(el)[kind];
  if (typeof url === "string" && url) postCommand(url, payload);
}

function runtimeUrls() {
  const script = document.currentScript;
  const fromMod = typeof import.meta !== "undefined" && import.meta.url ? import.meta.url : "";
  const base = fromMod || (script && script.src) || "";
  return {
    js: new URL("../assets/maplibre/maplibre-gl-csp.js", base).href,
    worker: new URL("../assets/maplibre/maplibre-gl-csp-worker.js", base).href,
    css: new URL("../assets/maplibre/maplibre-gl.css", base).href,
  };
}

function ensureCss(href) {
  if (document.querySelector('link[data-hedron-maplibre="css"]')) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = href;
  link.setAttribute("data-hedron-maplibre", "css");
  document.head.appendChild(link);
}

function loadScript(src, signal) {
  return new Promise((resolve, reject) => {
    const fail = () => reject(new Error("maplibre-load"));
    if (signal && signal.aborted) {
      fail();
      return;
    }
    if (signal) {
      signal.addEventListener("abort", fail, { once: true });
    }
    if (window.maplibregl) {
      resolve(window.maplibregl);
      return;
    }
    let existing = document.querySelector('script[data-hedron-maplibre="runtime"]');
    if (existing) {
      const failed =
        existing.getAttribute("data-hedron-maplibre-error") === "1" ||
        (existing.complete && !window.maplibregl);
      if (failed) {
        existing.remove();
        existing = null;
      }
    }
    if (existing) {
      existing.addEventListener("load", () => resolve(window.maplibregl), { once: true, signal });
      existing.addEventListener(
        "error",
        () => {
          existing.setAttribute("data-hedron-maplibre-error", "1");
          existing.remove();
          fail();
        },
        { once: true, signal }
      );
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.defer = true;
    script.setAttribute("data-hedron-maplibre", "runtime");
    script.addEventListener("load", () => resolve(window.maplibregl), { once: true, signal });
    script.addEventListener(
      "error",
      () => {
        script.setAttribute("data-hedron-maplibre-error", "1");
        script.remove();
        fail();
      },
      { once: true, signal }
    );
    document.head.appendChild(script);
  });
}

function colorMode() {
  if (window.matchMedia && window.matchMedia("(forced-colors: active)").matches) {
    return "forced-colors";
  }
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }
  return "light";
}

function reducedMotion() {
  return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
}

function dispose(el) {
  const state = bags.get(el);
  if (!state) return;
  state.gen += 1;
  try {
    state.ac.abort();
  } catch (_) {}
  state.ac = new AbortController();
  if (state.timer) {
    clearTimeout(state.timer);
    state.timer = 0;
  }
  if (state.ro) {
    try {
      state.ro.disconnect();
    } catch (_) {}
    state.ro = null;
  }
  if (state.map && typeof state.map.remove === "function") {
    try {
      state.map.remove();
    } catch (_) {}
  }
  state.map = null;
  el.removeAttribute("data-hedron-map-mounted");
}

function hostNode(el) {
  let host = el.querySelector("[data-hedron-map-host]");
  if (!host) {
    host = document.createElement("div");
    host.setAttribute("data-hedron-map-host", "1");
    host.setAttribute("tabindex", "0");
    host.className = "hedron-map-canvas";
    el.insertBefore(host, el.firstChild);
  }
  return host;
}

async function enhance(el, plan, gen, signal) {
  const urls = runtimeUrls();
  ensureCss(urls.css);
  let gl;
  try {
    gl = await loadScript(urls.js, signal);
  } catch (_) {
    emit(el, "map-failed", { code: "HED-MAP-RUNTIME-0001", message: "MapLibre failed to load" });
    return;
  }
  if (!gl || gen !== bag(el).gen || signal.aborted) return;
  gl.workerUrl = urls.worker;
  const host = hostNode(el);
  host.style.minHeight = "240px";
  const view = plan.view || {};
  const center = view.center || [0, 0];
  const style = plan.style && Object.keys(plan.style.sources || {}).length ? plan.style : {
    version: 8,
    sources: {},
    layers: [{ id: "background", type: "background", paint: { "background-color": "#e2e8f0" } }],
  };
  try {
    const map = new gl.Map({
      container: host,
      style,
      center: [Number(center[1]) || 0, Number(center[0]) || 0],
      zoom: Number(view.zoom) || 2,
      interactive: !reducedMotion(),
      attributionControl: true,
      fadeDuration: reducedMotion() ? 0 : 300,
      cooperativeGestures: true,
    });
    bag(el).map = map;
    map.on("load", () => emit(el, "map-loaded", { ok: true, mode: colorMode() }));
    map.on("error", (err) =>
      emit(el, "map-failed", { code: "HED-MAP-RUNTIME-0001", message: String(err && err.error || err) })
    );
    map.on("moveend", () => {
      const state = bag(el);
      if (state.timer) clearTimeout(state.timer);
      state.timer = setTimeout(() => {
        state.timer = 0;
        if (gen !== bag(el).gen || !bag(el).map) return;
        const b = map.getBounds();
        emit(el, "viewport-changed", {
          west: b.getWest(),
          south: b.getSouth(),
          east: b.getEast(),
          north: b.getNorth(),
          zoom: map.getZoom(),
          trigger: "map.viewport",
        });
      }, (plan.limits && plan.limits.viewport_debounce_ms) || 250);
    });
    map.on("click", (ev) => {
      const feats = map.queryRenderedFeatures(ev.point) || [];
      const ids = feats.map((f) => String((f.properties && (f.properties.id || f.properties.name)) || f.id || "")).filter(Boolean);
      if (ids.length) emit(el, "feature-selected", { ids: ids.slice(0, 100) });
    });
    host.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape") {
        host.blur();
        ev.preventDefault();
      }
      if (ev.key === "Enter" && bag(el).map) {
        emit(el, "feature-activated", { id: "keyboard" });
      }
    });
  } catch (err) {
    emit(el, "map-failed", { code: "HED-MAP-RUNTIME-0001", message: String(err) });
  }
}

function mount(el) {
  dispose(el);
  const state = bag(el);
  const gen = state.gen;
  const plan = parsePlan(el);
  if (!plan) {
    el.setAttribute("data-hedron-map-error", "missing or invalid MapPlan payload");
    emit(el, "map-failed", { code: "HED-MAP-RUNTIME-0002", message: "invalid MapPlan" });
    el.setAttribute("data-hedron-map-mounted", "1");
    return;
  }
  hostNode(el);
  el.setAttribute("data-hedron-map-mounted", "1");
  const lazy = !plan.renderer || plan.renderer.lazy !== false;
  const start = () => {
    if (gen !== bag(el).gen) return;
    enhance(el, plan, gen, bag(el).ac.signal);
  };
  if (!lazy || typeof IntersectionObserver === "undefined") {
    start();
    return;
  }
  const io = new IntersectionObserver((entries) => {
    if (entries.some((entry) => entry.isIntersecting)) {
      io.disconnect();
      start();
    }
  });
  io.observe(el);
  state.ro = io;
}

class HedronMap extends HTMLElement {
  static get observedAttributes() {
    return ["data-hedron-payload"];
  }
  connectedCallback() {
    mount(this);
  }
  disconnectedCallback() {
    dispose(this);
  }
  attributeChangedCallback() {
    if (this.isConnected) mount(this);
  }
}

if (!customElements.get(TAG)) {
  customElements.define(TAG, HedronMap);
}

function scan(root) {
  const base = root || document;
  if (base.matches && base.matches(TAG)) mount(base);
  if (base.querySelectorAll) base.querySelectorAll(TAG).forEach(mount);
}
function beforeSwap(ev) {
  const target = ev && ev.target;
  if (!target) return;
  if (target.matches && target.matches(TAG)) dispose(target);
  if (target.querySelectorAll) target.querySelectorAll(TAG).forEach(dispose);
}
function oobTarget(ev) {
  return (ev && ev.detail && ev.detail.elt) || (ev && ev.target) || null;
}
function beforeCleanup(ev) {
  const target = (ev && ev.detail && ev.detail.elt) || (ev && ev.target);
  if (target) beforeSwap({ target });
}

document.addEventListener("DOMContentLoaded", () => scan(document));
document.addEventListener("htmx:afterSwap", (ev) => scan(ev.target));
document.addEventListener("htmx:beforeSwap", beforeSwap);
document.addEventListener("htmx:oobAfterSwap", (ev) => scan(oobTarget(ev)));
document.addEventListener("htmx:oobBeforeSwap", (ev) => beforeSwap({ target: oobTarget(ev) }));
document.addEventListener("htmx:load", (ev) => scan(ev.target));
document.body && document.body.addEventListener("htmx:beforeCleanupElement", beforeCleanup);
