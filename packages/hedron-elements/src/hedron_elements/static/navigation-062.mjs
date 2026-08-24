/** Progressive navigation adapter for phase 0.62.
 *
 * It is opt-in and never replaces ordinary link navigation.  The server remains
 * authoritative; this module only applies a response for the active generation.
 */

const ACTIVE_ROOTS = new WeakMap();

export const NavigationPhases = Object.freeze([
  "idle",
  "pending",
  "committed",
  "rejected",
  "cancelled",
  "stale",
]);

export async function runViewTransition(update, { documentRoot = globalThis.document, enabled = false, reducedMotion = false } = {}) {
  if (!enabled || reducedMotion || typeof documentRoot?.startViewTransition !== "function") {
    return update();
  }
  const transition = documentRoot.startViewTransition(update);
  await transition.finished?.catch?.(() => {});
  return transition;
}

function sameIdentity(a, b) {
  return Boolean(a && b && a.navigationId === b.navigationId && a.generation === b.generation && a.target === b.target);
}

export function isSafeNavigationUrl(value, { origin = globalThis.location?.origin, sameOriginOnly = true } = {}) {
  try {
    const url = new URL(value, origin);
    if (!["http:", "https:"].includes(url.protocol) || url.username || url.password) return false;
    return !sameOriginOnly || url.origin === origin;
  } catch (_) {
    return false;
  }
}

export function decidePrefetch({ enabled = false, method = "GET", url, origin, concurrent = 0, maxConcurrent = 2, privateResponse = false } = {}) {
  if (!enabled) return { allowed: false, reason: "prefetch_disabled" };
  if (!["GET", "HEAD"].includes(String(method).toUpperCase())) return { allowed: false, reason: "unsafe_method" };
  if (!isSafeNavigationUrl(url, { origin, sameOriginOnly: true })) return { allowed: false, reason: "unsafe_origin" };
  if (concurrent >= maxConcurrent) return { allowed: false, reason: "max_concurrent" };
  if (privateResponse) return { allowed: false, reason: "private_response" };
  return { allowed: true, reason: "allowed" };
}

export class NavigationController {
  #generation = -1;
  #state = Object.freeze({ phase: "idle", identity: null, title: null, reason: null });

  get state() { return this.#state; }

  start(url, { navigationId = globalThis.crypto?.randomUUID?.() || String(Date.now()), target = "document" } = {}) {
    this.#generation += 1;
    const identity = Object.freeze({ navigationId, generation: this.#generation, url: String(url), target });
    this.#state = Object.freeze({ phase: "pending", identity, title: null, reason: null });
    return identity;
  }

  #matches(identity) {
    return this.#state.phase === "pending" && sameIdentity(this.#state.identity, identity);
  }

  #finish(identity, phase, reason, title = null) {
    if (!this.#matches(identity)) {
      return Object.freeze({ accepted: false, state: this.#state, reason: "stale_or_duplicate", diagnosticCode: "HED-NAV-0005" });
    }
    this.#state = Object.freeze({ phase, identity, title, reason });
    return Object.freeze({ accepted: true, state: this.#state, reason });
  }

  commit(identity, title = null) { return this.#finish(identity, "committed", "committed", title); }
  reject(identity, reason = "rejected") { return this.#finish(identity, "rejected", reason); }
  cancel(identity) { return this.#finish(identity, "cancelled", "cancelled"); }
}

function applyFragment(documentRoot, targetSelector, html, title) {
  const target = documentRoot.querySelector?.(targetSelector);
  if (!target) return false;
  const template = documentRoot.createElement?.("template");
  if (!template) return false;
  template.innerHTML = html;
  target.replaceChildren(...template.content.childNodes);
  if (title) documentRoot.title = title;
  target.querySelector?.("[data-hedron-focus], [aria-invalid=true], h1, main")?.focus?.({ preventScroll: true });
  return true;
}

export function enhanceNavigation062(root = document, { fetcher = globalThis.fetch, controller = new NavigationController(), prefetch = false } = {}) {
  if (!root || ACTIVE_ROOTS.has(root)) return ACTIVE_ROOTS.get(root)?.controller || controller;
  const cleanups = [];
  const prefetches = new Map();
  const onClick = async (event) => {
    const link = event.target?.closest?.("a[data-hedron-navigation='enhance'][href]");
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href, globalThis.location?.href);
    if (!isSafeNavigationUrl(url.href) || link.target || link.hasAttribute("download")) return;
    const target = link.dataset.hedronTarget || "main";
    if (!root.querySelector?.(target)) return;
    event.preventDefault();
    const identity = controller.start(url.href, { target });
    try {
      const response = await fetcher(url.href, { method: "GET", headers: { "X-Hedron-Navigation": "1" } });
      if (!response?.ok || !controller.state.identity || !sameIdentity(controller.state.identity, identity)) {
        controller.reject(identity, "response_rejected");
        globalThis.location?.assign?.(url.href);
        return;
      }
      const html = await response.text();
      const title = response.headers?.get?.("X-Hedron-Title") || html.match(/<title[^>]*>([^<]*)<\/title>/i)?.[1] || null;
      let applied = false;
      await runViewTransition(
        () => { applied = applyFragment(root, target, html, title); },
        { documentRoot: root, enabled: link.dataset.hedronTransition === "true" },
      );
      if (!applied) {
        controller.reject(identity, "target_missing");
        globalThis.location?.assign?.(url.href);
        return;
      }
      history.pushState({ hedronGeneration: identity.generation }, "", url.href);
      controller.commit(identity, title);
    } catch (_) {
      controller.reject(identity, "request_failed");
      globalThis.location?.assign?.(url.href);
    }
  };
  root.addEventListener("click", onClick);
  cleanups.push(() => root.removeEventListener("click", onClick));
  const onPopState = () => globalThis.location?.assign?.(globalThis.location.href);
  globalThis.addEventListener?.("popstate", onPopState);
  cleanups.push(() => globalThis.removeEventListener?.("popstate", onPopState));

  if (prefetch) {
    const onPointer = (event) => {
      const link = event.target?.closest?.("a[data-hedron-prefetch='true'][href]");
      if (!link || !isSafeNavigationUrl(link.href)) return;
      if (prefetches.has(link.href) || prefetches.size >= 2) return;
      const controller = new AbortController();
      prefetches.set(link.href, controller);
      void fetcher(link.href, {
        method: "GET",
        headers: { "X-Hedron-Prefetch": "1" },
        credentials: "same-origin",
        signal: controller.signal,
      }).catch(() => {}).finally(() => prefetches.delete(link.href));
    };
    root.addEventListener("pointerover", onPointer);
    cleanups.push(() => root.removeEventListener("pointerover", onPointer));
  }
  const registration = {
    controller,
    cleanup: () => {
      prefetches.forEach((request) => request.abort());
      prefetches.clear();
      cleanups.splice(0).forEach((cleanup) => cleanup());
      ACTIVE_ROOTS.delete(root);
    },
  };
  ACTIVE_ROOTS.set(root, registration);
  return controller;
}
