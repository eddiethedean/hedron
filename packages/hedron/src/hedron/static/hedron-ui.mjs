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
  if (!(trigger instanceof HTMLElement)) return;
  const dialog = dialogFromTrigger(trigger);
  if (!dialog) return;
  if (dialog.dataset.modal === "false") dialog.show();
  else dialog.showModal();
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

document.body.addEventListener("htmx:afterSwap", (event) => normalizeTabs(event.target));
normalizeTabs(document);
