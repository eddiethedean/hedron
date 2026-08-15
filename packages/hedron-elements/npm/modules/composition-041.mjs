/** Phase 0.41 typed composition, bounded draft transfer, navigation and traces. */
const EDGES = new Map();
const ACTIVE = new Map();
const MAX_AGGREGATE = 262144;

function plainObject(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const proto = Object.getPrototypeOf(value);
  return proto === Object.prototype || proto === null;
}

function byteLength(value) {
  return new TextEncoder().encode(JSON.stringify(value)).length;
}

export function registerCompositionEdge(edge) {
  if (!plainObject(edge) || !/^[A-Za-z][\w.:-]{0,127}$/.test(edge.id || "")) throw new TypeError("invalid edge");
  if (EDGES.has(edge.id)) throw new Error(`duplicate edge ${edge.id}`);
  for (const key of ["event", "action", "target"]) if (typeof edge[key] !== "string" || !edge[key]) throw new TypeError(`invalid ${key}`);
  edge.maxDepth = Math.min(32, Math.max(1, Number(edge.maxDepth || 8)));
  edge.maxPayloadBytes = Math.min(65536, Math.max(1, Number(edge.maxPayloadBytes || 16384)));
  edge.detailKeys = Object.freeze([...(edge.detailKeys || [])]);
  EDGES.set(edge.id, Object.freeze({ ...edge }));
}

export function clearCompositionEdges() { EDGES.clear(); }

export async function dispatchComposition(edgeId, event, handlers, context = {}) {
  const edge = EDGES.get(edgeId);
  if (!edge) return { outcome: "fallback", code: "HED-COMPOSE-0001" };
  const detail = event?.detail;
  if (!plainObject(detail) || Object.keys(detail).some((k) => !edge.detailKeys.includes(k)) || byteLength(detail) > edge.maxPayloadBytes) {
    return { outcome: "fallback", code: "HED-COMPOSE-0002" };
  }
  const visited = new Set(context.visited || []);
  if (visited.has(edge.id) || visited.size >= edge.maxDepth) return { outcome: "fallback", code: "HED-COMPOSE-0003" };
  visited.add(edge.id);
  if (typeof handlers?.authorize === "function" && !(await handlers.authorize(edge, event))) return { outcome: "fallback", code: "HED-COMPOSE-0004" };
  if (typeof handlers?.action !== "function") return { outcome: "fallback", code: "HED-COMPOSE-0005" };
  if (edge.concurrency === "drop" && ACTIVE.has(edge.id)) return { outcome: "canceled", code: "HED-COMPOSE-0006" };
  if (edge.concurrency === "replace") ACTIVE.get(edge.id)?.abort();
  const controller = new AbortController(); ACTIVE.set(edge.id, controller);
  try {
    const result = await handlers.action(edge.action, detail, { edge, visited, signal: controller.signal });
    return { outcome: "success", result };
  } catch (_) { return { outcome: controller.signal.aborted ? "canceled" : "error", code: "HED-COMPOSE-0007" }; }
  finally { if (ACTIVE.get(edge.id) === controller) ACTIVE.delete(edge.id); }
}

export function draftStorageKey(identity) {
  const required = ["app", "routeFamily", "elementContract", "schemaVersion", "subject"];
  if (!plainObject(identity) || required.some((key) => typeof identity[key] !== "string" || !identity[key])) throw new TypeError("invalid draft identity");
  return `hedron:draft:v1:${required.map((key) => encodeURIComponent(identity[key])).join(":")}`;
}

function validDraft(envelope, now = Date.now()) {
  if (!plainObject(envelope) || envelope.version !== 1 || !plainObject(envelope.fields)) return false;
  if (!Number.isFinite(envelope.expiresAt) || envelope.expiresAt <= now || envelope.expiresAt - envelope.createdAt > 1800000) return false;
  const forbidden = /auth|authorization|cookie|csrf|file|html|password|secret|token/i;
  return !Object.keys(envelope.fields).some((key) => forbidden.test(key));
}

export function storeDraft(identity, fields, options = {}) {
  try {
    const storage = options.storage || sessionStorage;
    const now = options.now || Date.now();
    const envelope = { version: 1, ...identity, fields: { ...fields }, operationId: options.operationId || crypto.randomUUID(), createdAt: now, expiresAt: now + Math.min(1800000, Math.max(1, options.ttlMs || 300000)) };
    if (!validDraft(envelope, now)) return false;
    const raw = JSON.stringify(envelope);
    if (new TextEncoder().encode(raw).length > 32768) return false;
    let total = raw.length;
    for (let i = 0; i < storage.length; i += 1) { const key = storage.key(i); if (key?.startsWith("hedron:draft:v1:")) total += (storage.getItem(key) || "").length; }
    if (total > MAX_AGGREGATE) return false;
    storage.setItem(draftStorageKey(identity), raw); return true;
  } catch (_) { return false; }
}

export function consumeDraft(identity, options = {}) {
  try {
    const storage = options.storage || sessionStorage; const key = draftStorageKey(identity); const raw = storage.getItem(key); storage.removeItem(key);
    if (!raw) return null; const envelope = JSON.parse(raw);
    if (!validDraft(envelope, options.now || Date.now())) return null;
    for (const field of options.allowedFields || []) if (!Object.hasOwn(envelope.fields, field)) continue;
    if (options.allowedFields) envelope.fields = Object.fromEntries(Object.entries(envelope.fields).filter(([key]) => options.allowedFields.includes(key)));
    return envelope;
  } catch (_) { return null; }
}

export function clearDrafts(options = {}) {
  try { const storage = options.storage || sessionStorage; for (let i = storage.length - 1; i >= 0; i -= 1) { const key = storage.key(i); if (key?.startsWith("hedron:draft:v1:")) storage.removeItem(key); } } catch (_) {}
}

export function emitBrowserTrace(trace, sink) {
  const allowed = ["correlationId", "elementId", "edgeId", "operationId", "outcome", "diagnosticCode", "durationMs"];
  if (!plainObject(trace) || Object.keys(trace).some((key) => !allowed.includes(key)) || byteLength(trace) > 4096) return false;
  try { sink?.(Object.freeze({ ...trace })); return true; } catch (_) { return false; }
}

export function enhanceNavigation(root = document) {
  root.addEventListener("click", (event) => {
    const link = event.target?.closest?.("a[href]"); if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href, location.href); if (url.origin !== location.origin || link.target || link.hasAttribute("download")) return;
    if (url.pathname === location.pathname && url.search === location.search && url.hash) { event.preventDefault(); history.pushState(history.state, "", url); document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView(); }
  });
  root.addEventListener("htmx:afterSwap", (event) => { const title = event.detail?.xhr?.getResponseHeader?.("X-Hedron-Title"); if (title) document.title = title; const target = event.detail?.target; target?.querySelector?.("[data-hedron-focus], [aria-invalid=true], h1, main")?.focus?.({ preventScroll: true }); });
}
