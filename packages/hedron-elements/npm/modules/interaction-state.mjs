/** InteractionState machine (phase 0.61 / ACTIONSTATE-061). */
export const InteractionStates = Object.freeze([
  "idle",
  "pending",
  "success",
  "error",
  "cancelled",
  "canceled",
  "stale",
  "conflict",
]);

export class InteractionState {
  #state = "idle";
  #operationId = null;
  #progress = 0;
  #updatedAt = 0;
  #policy = "drop";
  #generation = 0;

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

  get generation() {
    return this.#generation;
  }

  begin(operationId) {
    if (this.#state === "pending") {
      if (this.#policy === "drop") return false;
      if (this.#policy === "replace") this.cancel();
      else return false;
    }
    this.#operationId = operationId || crypto.randomUUID?.() || String(Date.now());
    this.#generation += 1;
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
    return this.complete("success");
  }

  fail() {
    return this.complete("error");
  }

  cancel() {
    return this.complete("cancelled");
  }

  stale() {
    return this.complete("stale");
  }

  conflict() {
    return this.complete("conflict");
  }

  complete(phase, { operationId = this.#operationId, generation = this.#generation } = {}) {
    if (this.#state !== "pending") return false;
    if (operationId !== this.#operationId || generation !== this.#generation) return false;
    if (!["success", "error", "cancelled", "stale", "conflict"].includes(phase)) return false;
    this.#state = phase;
    if (phase === "success") this.#progress = 100;
    this.#updatedAt = Date.now();
    return true;
  }

  reset() {
    this.#state = "idle";
    this.#operationId = null;
    this.#progress = 0;
    this.#generation = 0;
    this.#updatedAt = Date.now();
  }

  applyAria(el) {
    if (!el) return;
    el.setAttribute("aria-busy", this.#state === "pending" ? "true" : "false");
    el.setAttribute("data-hedron-action-phase", this.#state);
    el.setAttribute("data-hedron-action-generation", String(this.#generation));
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
