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

function activateTab(tab, { focus = true } = {}) {
  const tabs = tab.closest(".hedron-tabs");
  if (!(tabs instanceof HTMLElement)) return;

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
    const selected =
      controls.find((tab) => tab.getAttribute("aria-selected") === "true") || controls[0];
    activateTab(selected, { focus: false });
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
    }
    return;
  }

  const dismiss = event.target.closest("[data-hedron-toast-dismiss]");
  if (dismiss instanceof HTMLElement) {
    dismiss.closest("[data-hedron-toast]")?.remove();
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
  activateTab(controls[next]);
});

document.body.addEventListener("htmx:afterSwap", (event) => {
  normalizeTabs(event.target);
  upgradeOpenModalDialogs(event.target);
  const source = event.detail?.requestConfig?.elt;
  const load = source instanceof Element ? source.getAttribute("data-hedron-after-load") : null;
  if (load && typeof window.htmx?.ajax === "function") {
    window.htmx.ajax("GET", load, { source, swap: "none" });
  }
});
normalizeTabs(document);
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

document.body.addEventListener("htmx:afterSwap", (event) => {
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

document.body.addEventListener("htmx:responseError", (event) => {
  applyErrorTemplate(event.detail?.elt);
});
document.body.addEventListener("htmx:sendError", (event) => {
  applyErrorTemplate(event.detail?.elt);
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

document.body.addEventListener("htmx:beforeRequest", (event) => {
  const marked = busyMarked(event.detail?.elt);
  if (marked) setBusy(marked, true);
});
document.body.addEventListener("htmx:afterRequest", (event) => {
  const marked = busyMarked(event.detail?.elt);
  if (marked) setBusy(marked, false);
});
document.body.addEventListener("htmx:afterSwap", (event) => {
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


