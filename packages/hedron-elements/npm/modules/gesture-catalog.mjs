/** GestureOverlayCatalog primitives (phase 0.37 / INTERACT-037). */
const OVERLAY_KINDS = Object.freeze([
  "dialog",
  "popover",
  "menu",
  "combobox",
  "tooltip",
  "command",
  "toast",
]);

export class GestureOverlayCatalog {
  #entries = new Map();

  register(kind, handler) {
    if (!OVERLAY_KINDS.includes(kind)) throw new Error(`Unknown overlay kind: ${kind}`);
    this.#entries.set(kind, handler);
  }

  open(kind, intent) {
    const handler = this.#entries.get(kind);
    if (!handler) throw new Error(`Overlay not registered: ${kind}`);
    if (intent == null || typeof intent !== "object") throw new Error("Intent must be an object");
    if ("url" in intent || "selector" in intent) throw new Error("Intent must not carry raw URLs/selectors");
    return handler.open(intent);
  }

  close(kind) {
    const handler = this.#entries.get(kind);
    handler?.close?.();
  }

  dispose() {
    for (const handler of this.#entries.values()) handler.dispose?.();
    this.#entries.clear();
  }
}

export const catalog = new GestureOverlayCatalog();

catalog.register("dialog", {
  open(intent) {
    const dlg = document.createElement("dialog");
    dlg.textContent = String(intent.label || "Dialog");
    document.body.appendChild(dlg);
    dlg.showModal();
    return dlg;
  },
  close() {
    document.querySelector("dialog[open]")?.close?.();
  },
  dispose() {
    document.querySelectorAll("dialog[data-hedron-catalog]").forEach((node) => node.remove());
  },
});

export function pointerOrKeyboard(event, keyboardEquivalent) {
  if (event.type.startsWith("key") && typeof keyboardEquivalent === "function") {
    keyboardEquivalent(event);
    return true;
  }
  return false;
}
