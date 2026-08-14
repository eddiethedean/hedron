/**
 * Shared Hedron element bridge (phase 0.36).
 * Owns early HTMX cleanup hooks and typed-event allowlisting.
 * Keep gzip size ≤ 12 KiB.
 */
const OWNED = new WeakMap();

export function track(el, resources) {
  const bag = OWNED.get(el) || { ac: null, listeners: [], timers: [] };
  if (!bag.ac) bag.ac = new AbortController();
  OWNED.set(el, bag);
  if (resources?.listener) bag.listeners.push(resources.listener);
  if (resources?.timer != null) bag.timers.push(resources.timer);
  return bag.ac.signal;
}

export function dispose(el) {
  const bag = OWNED.get(el);
  if (!bag) return;
  try {
    bag.ac?.abort();
  } catch (_) {}
  for (const t of bag.timers || []) clearTimeout(t);
  bag.timers = [];
  bag.listeners = [];
  OWNED.delete(el);
}

export function validateEventDetail(detail, schemaKeys) {
  if (detail == null || typeof detail !== "object") return false;
  if (
    Object.hasOwn(detail, "__proto__") ||
    Object.hasOwn(detail, "constructor") ||
    Object.hasOwn(detail, "prototype")
  ) {
    return false;
  }
  for (const key of Object.keys(detail)) {
    if (schemaKeys && !schemaKeys.includes(key)) return false;
    const v = detail[key];
    if (typeof v === "function") return false;
    if (typeof Node !== "undefined" && v instanceof Node) return false;
  }
  return true;
}

function onBeforeCleanup(ev) {
  const root = ev?.detail?.elt || ev?.target;
  if (!root) return;
  if (root.tagName && String(root.tagName).toLowerCase().startsWith("hedron-")) {
    dispose(root);
  }
  root.querySelectorAll?.("[data-hedron-element]").forEach((node) => dispose(node));
}

if (typeof document !== "undefined") {
  document.body?.addEventListener?.("htmx:beforeCleanupElement", onBeforeCleanup);
  document.addEventListener("htmx:beforeSwap", (ev) => {
    const t = ev.target || document;
    t.querySelectorAll?.("[data-hedron-element]").forEach((node) => dispose(node));
  });
}

export const HEDRON_BRIDGE_VERSION = 1;
