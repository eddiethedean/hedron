/**
 * Small, HTMX-safe enhancements for Hedron's semantic interaction built-ins.
 * Event delegation keeps nested components working after fragment swaps without
 * per-instance listener bookkeeping.
 */

function ownedTabs(tabs) {
  return Array.from(tabs.querySelectorAll(":scope > .hedron-tablist > [role='tab']"));
}

function ownedPanels(tabs) {
  return Array.from(tabs.querySelectorAll(":scope > [role='tabpanel']"));
}

function alpineOwnsTabs(tabs) {
  return tabs.hasAttribute("x-data") || tabs.querySelector("[x-data]") !== null;
}

function activateTab(tab, { focus = true } = {}) {
  const tabs = tab.closest(".hedron-tabs");
  if (!(tabs instanceof HTMLElement)) return;
  if (alpineOwnsTabs(tabs)) {
    if (focus) tab.focus();
    return;
  }

  const controls = tab.getAttribute("aria-controls");
  for (const candidate of ownedTabs(tabs)) {
    const selected = candidate === tab;
    candidate.setAttribute("aria-selected", selected ? "true" : "false");
    candidate.setAttribute("tabindex", selected ? "0" : "-1");
  }
  for (const panel of ownedPanels(tabs)) {
    panel.hidden = panel.id !== controls;
  }
  if (focus) tab.focus();
  tabs.dispatchEvent(
    new CustomEvent("hedron:tab-change", {
      bubbles: true,
      detail: { tabId: tab.id, panelId: controls },
    }),
  );
}

function normalizeTabs(root) {
  const sets = [];
  if (root instanceof Element && root.matches(".hedron-tabs")) sets.push(root);
  root.querySelectorAll?.(".hedron-tabs").forEach((tabs) => sets.push(tabs));

  for (const tabs of sets) {
    const controls = ownedTabs(tabs);
    if (!controls.length) continue;
    if (alpineOwnsTabs(tabs)) continue;
    const selected =
      controls.find((tab) => tab.getAttribute("aria-selected") === "true") || controls[0];
    activateTab(selected, { focus: false });
  }
}

function setNavCollapsed(shell, collapsed, persist = true) {
  if (!(shell instanceof HTMLElement)) return;
  shell.dataset.hedronNavCollapsed = collapsed ? "true" : "false";
  const toggle = shell.querySelector("[data-hedron-nav-toggle]");
  if (toggle instanceof HTMLElement) {
    toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
    toggle.textContent = collapsed ? "Expand navigation" : "Collapse navigation";
  }
  if (persist) {
    const key = shell.querySelector("[data-hedron-nav-preference]")?.getAttribute("data-hedron-nav-preference");
    try { if (key) localStorage.setItem(key, collapsed ? "true" : "false"); } catch (_) { /* storage may be disabled */ }
  }
}

function normalizeNavCollapse(root) {
  const shells = [];
  if (root instanceof Element && root.matches(".hedron-app-shell[data-hedron-nav-collapse='user']")) shells.push(root);
  root.querySelectorAll?.(".hedron-app-shell[data-hedron-nav-collapse='user']").forEach((shell) => shells.push(shell));
  for (const shell of shells) {
    const key = shell.querySelector("[data-hedron-nav-preference]")?.getAttribute("data-hedron-nav-preference");
    try {
      const saved = key ? localStorage.getItem(key) : null;
      if (saved === "true" || saved === "false") setNavCollapsed(shell, saved === "true", false);
    } catch (_) { /* storage may be disabled */ }
  }
}

function dialogFromTrigger(trigger) {
  const selector = trigger.getAttribute("data-hedron-dialog-open");
  if (!selector || !/^#[A-Za-z][\w:.-]*$/.test(selector)) return null;
  const dialog = document.querySelector(selector);
  return dialog instanceof HTMLDialogElement ? dialog : null;
}

document.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;
  const tab = event.target.closest("[role='tab']");
  if (tab instanceof HTMLElement && tab.closest(".hedron-tabs")) {
    activateTab(tab);
    return;
  }

  const trigger = event.target.closest("[data-hedron-dialog-open]");
  if (trigger instanceof HTMLElement) {
    const dialog = dialogFromTrigger(trigger);
    if (dialog) {
      if (dialog.dataset.modal === "false") dialog.show();
      else dialog.showModal();
      dialog.dispatchEvent(new CustomEvent("hedron-dialog-open", { bubbles: true }));
    }
    return;
  }

  const dismiss = event.target.closest("[data-hedron-toast-dismiss]");
  if (dismiss instanceof HTMLElement) {
    dismiss.closest("[data-hedron-toast]")?.remove();
    return;
  }

  const navToggle = event.target.closest("[data-hedron-nav-toggle]");
  if (navToggle instanceof HTMLElement) {
    const shell = navToggle.closest(".hedron-app-shell");
    if (shell instanceof HTMLElement) {
      setNavCollapsed(shell, shell.dataset.hedronNavCollapsed !== "true");
    }
  }
});

document.addEventListener("keydown", (event) => {
  if (!(event.target instanceof HTMLElement) || event.target.getAttribute("role") !== "tab") {
    return;
  }
  const tabs = event.target.closest(".hedron-tabs");
  if (!(tabs instanceof HTMLElement)) return;
  const controls = ownedTabs(tabs);
  const index = controls.indexOf(event.target);
  if (index < 0) return;

  let next = index;
  if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % controls.length;
  else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
    next = (index - 1 + controls.length) % controls.length;
  } else if (event.key === "Home") next = 0;
  else if (event.key === "End") next = controls.length - 1;
  else return;

  event.preventDefault();
  controls[next].focus();
  controls[next].click();
});

document.addEventListener("htmx:afterSwap", (event) => {
  normalizeTabs(event.target);
  normalizeNavCollapse(event.target);
  upgradeOpenModalDialogs(event.target);
  const source = event.detail?.requestConfig?.elt;
  const load = source instanceof Element ? source.getAttribute("data-hedron-after-load") : null;
  if (load && source instanceof Element) {
    // Compatibility notification only.  Hedron no longer starts a second
    // request from this lifecycle listener; applications should declare a
    // typed hx-trigger/hx-get companion for follow-up work.
    source.dispatchEvent(
      new CustomEvent("hedron:after-load", { bubbles: true, detail: { url: load } }),
    );
  }
});
normalizeTabs(document);
normalizeNavCollapse(document);
upgradeOpenModalDialogs(document);

function upgradeOpenModalDialogs(root) {
  const scope = root instanceof Document || root instanceof Element ? root : document;
  const dialogs = [];
  if (scope instanceof HTMLDialogElement) dialogs.push(scope);
  scope.querySelectorAll?.("dialog.hedron-dialog[data-modal='true']").forEach((d) => {
    dialogs.push(d);
  });
  for (const dialog of dialogs) {
    if (!(dialog instanceof HTMLDialogElement)) continue;
    // SSR ``open`` is non-modal; close then showModal for focus trap / backdrop.
    if (!dialog.hasAttribute("open") && !dialog.open) continue;
    if (typeof dialog.showModal !== "function") continue;
    try {
      dialog.close();
      dialog.showModal();
    } catch {
      // Not connected or already modal; ignore.
    }
  }
}

function toastHost() {
  return document.getElementById("hedron-toast");
}

function enqueueToast(node) {
  const host = toastHost();
  if (!(host instanceof HTMLElement) || !(node instanceof HTMLElement)) return;
  host.appendChild(node);
  const ttl = node.getAttribute("data-hedron-ttl");
  if (ttl) {
    const ms = Number(ttl);
    if (Number.isFinite(ms) && ms > 0) {
      window.setTimeout(() => node.remove(), ms);
    }
  }
}

function applyErrorTemplate(elt) {
  const host = elt instanceof Element ? elt.closest("[data-hedron-error-slot]") : null;
  if (!(host instanceof HTMLElement)) return;
  const tpl = host.querySelector("template[data-hedron-error-template]");
  if (!(tpl instanceof HTMLTemplateElement)) return;
  host.replaceChildren(tpl.content.cloneNode(true));
}

document.addEventListener("htmx:afterSwap", (event) => {
  const swapped = event.detail?.elt;
  if (swapped instanceof HTMLElement && swapped.matches("[data-hedron-toast]")) {
    enqueueToast(swapped);
  }
  const host = toastHost();
  if (host instanceof HTMLElement) {
    host.querySelectorAll("[data-hedron-toast]").forEach((node) => {
      if (node.parentElement !== host) enqueueToast(node);
    });
  }
});

document.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;
  const toggle = event.target.closest("[data-hedron-password-toggle]");
  if (!(toggle instanceof HTMLButtonElement)) return;
  event.preventDefault();
  if (toggle.disabled) return;
  const inputId = toggle.getAttribute("data-hedron-password-toggle") || toggle.getAttribute("aria-controls");
  const input = inputId ? document.getElementById(inputId) : toggle.parentElement?.querySelector("input");
  if (!(input instanceof HTMLInputElement) || input.disabled) return;
  const show = input.type === "password";
  input.type = show ? "text" : "password";
  toggle.setAttribute("aria-pressed", show ? "true" : "false");
  toggle.setAttribute("aria-label", show ? "Hide password" : "Show password");
  toggle.textContent = show ? "Hide password" : "Show password";
});

const busyCounts = new WeakMap();
const actionGenerations = new WeakMap();
const activeRequests = new WeakMap();

function busyMarked(elt) {
  if (!(elt instanceof Element)) return null;
  return elt.closest("[data-hedron-busy]");
}

function setBusy(marked, busy) {
  if (!(marked instanceof HTMLElement)) return;
  const next = (busyCounts.get(marked) || 0) + (busy ? 1 : -1);
  const count = Math.max(0, next);
  busyCounts.set(marked, count);
  const on = count > 0;
  const host =
    marked.getAttribute("data-hedron-busy") === "document"
      ? document.documentElement
      : marked;
  host.setAttribute("aria-busy", on ? "true" : "false");
  const indicatorSel = marked.getAttribute("data-hedron-busy-indicator");
  if (indicatorSel && /^#[A-Za-z][\w:.-]*$/.test(indicatorSel)) {
    const indicator = document.querySelector(indicatorSel);
    if (indicator instanceof HTMLElement) indicator.hidden = !on;
  }
}

function setActionPhase(elt, phase) {
  const marked = busyMarked(elt);
  if (!(marked instanceof HTMLElement)) return;
  if (phase === "pending") {
    const generation = (actionGenerations.get(marked) || 0) + 1;
    actionGenerations.set(marked, generation);
    marked.setAttribute("data-hedron-action-generation", String(generation));
  }
  marked.setAttribute("data-hedron-action-phase", phase);
}

function requestKey(detail) {
  return detail?.xhr || detail || null;
}

function finishRequest(event, phase, { error = false } = {}) {
  const elt = event.detail?.elt;
  const marked = busyMarked(elt);
  if (!(marked instanceof HTMLElement)) return;
  const key = requestKey(event.detail);
  if (activeRequests.get(marked) !== key) return;
  activeRequests.delete(marked);
  setActionPhase(elt, phase);
  setBusy(marked, false);
  if (error) applyErrorTemplate(elt);
}

document.addEventListener("htmx:beforeRequest", (event) => {
  const marked = busyMarked(event.detail?.elt);
  if (marked) {
    activeRequests.set(marked, requestKey(event.detail));
    setActionPhase(event.detail?.elt, "pending");
    setBusy(marked, true);
  }
});
document.addEventListener("htmx:afterRequest", (event) => {
  const status = event.detail?.xhr?.status || 0;
  finishRequest(event, status >= 200 && status < 400 ? "success" : "error", {
    error: !(status >= 200 && status < 400),
  });
});
document.addEventListener("htmx:responseError", (event) => {
  // finishRequest owns the exactly-once setBusy(false) cleanup.
  finishRequest(event, "error", { error: true });
});
document.addEventListener("htmx:sendError", (event) => {
  // finishRequest owns the exactly-once setBusy(false) cleanup.
  finishRequest(event, "error", { error: true });
});
document.addEventListener("htmx:sendAbort", (event) => finishRequest(event, "cancelled"));
document.addEventListener("htmx:timeout", (event) => finishRequest(event, "error", { error: true }));
document.addEventListener("htmx:afterSwap", (event) => {
  const root = event.target instanceof Element ? event.target : document;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const nodes = [];
  if (root instanceof Element && root.matches("[data-hedron-reveal='swap']")) nodes.push(root);
  root.querySelectorAll?.("[data-hedron-reveal='swap']").forEach((n) => nodes.push(n));
  for (const node of nodes) {
    if (!(node instanceof HTMLElement)) continue;
    if (reduced && node.getAttribute("data-hedron-reduced-motion") !== "ignore") {
      node.classList.add("is-revealed");
      continue;
    }
    node.classList.remove("is-revealed");
    requestAnimationFrame(() => node.classList.add("is-revealed"));
  }
});
