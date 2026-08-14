/** InteractionState machine (phase 0.37 / ACTIONSTATE-037). */
export const InteractionStates = Object.freeze([
  "idle",
  "pending",
  "success",
  "error",
  "canceled",
]);

export class InteractionState {
  #state = "idle";
  #operationId = null;
  #progress = 0;
  #updatedAt = 0;
  #policy = "drop";

  constructor({ policy = "drop" } = {}) {
    this.#policy = policy;
  }

  get state() {
    return this.#state;
  }

  get operationId() {
    return this.#operationId;
  }

  get progress() {
    return this.#progress;
  }

  begin(operationId) {
    if (this.#state === "pending") {
      if (this.#policy === "drop") return false;
      if (this.#policy === "replace") this.cancel();
      else return false;
    }
    this.#operationId = operationId || crypto.randomUUID?.() || String(Date.now());
    this.#state = "pending";
    this.#progress = 0;
    this.#updatedAt = Date.now();
    return true;
  }

  setProgress(value) {
    if (this.#state !== "pending") return;
    this.#progress = Math.max(0, Math.min(100, Number(value) || 0));
    this.#updatedAt = Date.now();
  }

  succeed() {
    if (this.#state !== "pending") return;
    this.#state = "success";
    this.#progress = 100;
    this.#updatedAt = Date.now();
  }

  fail() {
    if (this.#state !== "pending") return;
    this.#state = "error";
    this.#updatedAt = Date.now();
  }

  cancel() {
    if (this.#state !== "pending") return;
    this.#state = "canceled";
    this.#updatedAt = Date.now();
  }

  reset() {
    this.#state = "idle";
    this.#operationId = null;
    this.#progress = 0;
    this.#updatedAt = Date.now();
  }

  applyAria(el) {
    if (!el) return;
    el.setAttribute("aria-busy", this.#state === "pending" ? "true" : "false");
  }
}

export function bindHtmxInteractionState(el, machine, { pendingOn = "htmx:beforeRequest", doneOn = "htmx:afterRequest" } = {}) {
  const onPending = () => {
    if (!machine.begin()) return;
    machine.applyAria(el);
  };
  const onDone = (ev) => {
    const status = ev?.detail?.xhr?.status;
    if (status === 202) return;
    if (status >= 200 && status < 400) machine.succeed();
    else machine.fail();
    machine.applyAria(el);
  };
  el.addEventListener(pendingOn, onPending);
  el.addEventListener(doneOn, onDone);
  return () => {
    el.removeEventListener(pendingOn, onPending);
    el.removeEventListener(doneOn, onDone);
  };
}
