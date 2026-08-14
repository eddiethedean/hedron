/**
 * Experimental React-island reference (docs only).
 * Not part of hedron-elements runtime. No HTMX region ownership.
 */

const OWNED = new WeakMap();

export function mountIsland(root, props = {}) {
  if (!(root instanceof Element)) {
    throw new TypeError("island root must be an Element");
  }
  if (OWNED.has(root)) {
    throw new Error("island root already owned");
  }
  const state = { props: Object.freeze({ ...props }), disposed: false };
  OWNED.set(root, state);
  root.setAttribute("data-hedron-island", "experimental");
  root.removeAttribute("hx-target");
  root.removeAttribute("data-hedron-region");
  return {
    update(next) {
      if (state.disposed) throw new Error("island disposed");
      state.props = Object.freeze({ ...next });
    },
    unmount() {
      if (state.disposed) return;
      state.disposed = true;
      OWNED.delete(root);
      root.removeAttribute("data-hedron-island");
    },
  };
}

export function removalLedger() {
  return [
    "Remove island mount call sites",
    "Delete pinned island assets from CSP/supply inventory",
    "Confirm no hx-target / region ownership remains",
  ];
}
