/**
 * Minimal HTMX lifecycle bridge for Hedron request state.
 *
 * This module intentionally owns only request identity, busy state, action
 * phases, and error-template projection. Widget behavior belongs to
 * hedron-ui.mjs and is loaded separately when a widget demands it.
 */

if (!window.__hedronHtmxLifecycleInstalled) {
  window.__hedronHtmxLifecycleInstalled = true;

  const busyCounts = new WeakMap();
  const actionGenerations = new WeakMap();
  const activeRequests = new WeakMap();
  const requestsByMarker = new WeakMap();
  const markersByHost = new WeakMap();

  function busyMarked(elt) {
    if (!(elt instanceof Element)) return null;
    return elt.closest("[data-hedron-busy]");
  }

  function busyHost(marked) {
    return marked.getAttribute("data-hedron-busy") === "document"
      ? document.documentElement
      : marked;
  }

  function updateBusyIndicator(marked, on) {
    const selector = marked.getAttribute("data-hedron-busy-indicator");
    if (selector && /^#[A-Za-z][\w:.-]*$/.test(selector)) {
      const indicator = document.querySelector(selector);
      if (indicator instanceof HTMLElement) indicator.hidden = !on;
    }
  }

  function setBusyHost(host, busy) {
    const next = (busyCounts.get(host) || 0) + (busy ? 1 : -1);
    const count = Math.max(0, next);
    busyCounts.set(host, count);
    const on = count > 0;
    host.setAttribute("aria-busy", on ? "true" : "false");
    const markers = markersByHost.get(host);
    if (markers) {
      for (const marked of markers) updateBusyIndicator(marked, on);
      if (!on) markersByHost.delete(host);
    }
  }

  function registerBusyMarker(marked, host) {
    const markers = markersByHost.get(host) || new Set();
    markers.add(marked);
    markersByHost.set(host, markers);
  }

  function unregisterBusyMarker(marked, host) {
    const markers = markersByHost.get(host);
    if (!markers) return;
    markers.delete(marked);
    if (markers.size === 0) markersByHost.delete(host);
  }

  function setActionPhase(marked, phase) {
    if (marked instanceof HTMLElement) {
      marked.setAttribute("data-hedron-action-phase", phase);
    }
  }

  function requestKey(detail) {
    return detail?.xhr && typeof detail.xhr === "object" ? detail.xhr : null;
  }

  function applyErrorTemplate(elt) {
    const host = elt instanceof Element ? elt.closest("[data-hedron-error-slot]") : null;
    if (!(host instanceof HTMLElement)) return;
    const template = host.querySelector("template[data-hedron-error-template]");
    if (template instanceof HTMLTemplateElement) {
      host.replaceChildren(template.content.cloneNode(true));
    }
  }

  function finishRecord(record, phase, { error = false } = {}) {
    if (!record || record.finalized) return;
    record.finalized = true;
    activeRequests.delete(record.key);
    const records = requestsByMarker.get(record.marked);
    if (records) {
      records.delete(record);
      if (records.size === 0) {
        requestsByMarker.delete(record.marked);
      }
    }
    setBusyHost(record.host, false);
    if (record.host !== document.documentElement && (!records || records.size === 0)) {
      unregisterBusyMarker(record.marked, record.host);
    }
    if (actionGenerations.get(record.marked) === record.generation) {
      setActionPhase(record.marked, phase);
      if (error) applyErrorTemplate(record.elt);
    }
  }

  function finishRequest(event, phase, options = {}) {
    const key = requestKey(event.detail);
    finishRecord(key ? activeRequests.get(key) : null, phase, options);
  }

  document.addEventListener("htmx:beforeRequest", (event) => {
    const marked = busyMarked(event.detail?.elt);
    const key = requestKey(event.detail);
    if (!(marked instanceof HTMLElement) || !key) return;
    const generation = (actionGenerations.get(marked) || 0) + 1;
    actionGenerations.set(marked, generation);
    marked.setAttribute("data-hedron-action-generation", String(generation));
    setActionPhase(marked, "pending");
    const record = {
      key,
      elt: event.detail?.elt,
      marked,
      host: busyHost(marked),
      generation,
      finalized: false,
    };
    activeRequests.set(key, record);
    const records = requestsByMarker.get(marked) || new Set();
    records.add(record);
    requestsByMarker.set(marked, records);
    registerBusyMarker(marked, record.host);
    setBusyHost(record.host, true);
  });

  document.addEventListener("htmx:afterRequest", (event) => {
    const status = event.detail?.xhr?.status || 0;
    finishRequest(event, status >= 200 && status < 400 ? "success" : "error", {
      error: !(status >= 200 && status < 400),
    });
  });
  document.addEventListener("htmx:responseError", (event) =>
    finishRequest(event, "error", { error: true }),
  );
  document.addEventListener("htmx:sendError", (event) =>
    finishRequest(event, "error", { error: true }),
  );
  document.addEventListener("htmx:sendAbort", (event) => finishRequest(event, "cancelled"));
  document.addEventListener("htmx:timeout", (event) =>
    finishRequest(event, "error", { error: true }),
  );
  document.addEventListener("htmx:beforeCleanupElement", (event) => {
    const cleaned = event.detail?.elt;
    const marked = cleaned instanceof Element ? cleaned.closest("[data-hedron-busy]") : null;
    const records = marked instanceof HTMLElement ? requestsByMarker.get(marked) : null;
    if (!records) return;
    for (const record of [...records]) {
      if (cleaned === record.elt || (cleaned instanceof Element && cleaned.contains(record.elt))) {
        finishRecord(record, "cancelled");
      }
    }
  });
}
