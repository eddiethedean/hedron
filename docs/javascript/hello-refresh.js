(function () {
  "use strict";

  function utcStamp() {
    const now = new Date();
    const hh = String(now.getUTCHours()).padStart(2, "0");
    const mm = String(now.getUTCMinutes()).padStart(2, "0");
    const ss = String(now.getUTCSeconds()).padStart(2, "0");
    return `${hh}:${mm}:${ss} UTC`;
  }

  function statusMarkup(stamp) {
    const wrap = document.createElement("div");
    wrap.className = "hedron-browser-sim__status";
    wrap.id = "service-status";
    wrap.setAttribute("role", "status");
    wrap.setAttribute("aria-live", "polite");
    wrap.innerHTML =
      '<span class="hedron-browser-sim__status-icon" aria-hidden="true">✓</span>' +
      `<span data-hbs-stamp>All systems operational · refreshed ${stamp}</span>`;
    return wrap;
  }

  function delay(ms) {
    return new Promise((resolve) => {
      window.setTimeout(resolve, ms);
    });
  }

  function initSim(root) {
    if (root.dataset.hbsReady === "true") return;
    root.dataset.hbsReady = "true";

    const button = root.querySelector("[data-hbs-refresh]");
    const hint = root.querySelector("[data-hbs-hint]");
    const trace = root.querySelector("[data-hbs-trace]");
    let busy = false;

    // Seed an initial UTC stamp so the demo matches a live server.
    const region = root.querySelector("#service-status");
    if (region) {
      const stampNode = region.querySelector("[data-hbs-stamp]");
      if (stampNode) {
        stampNode.textContent = `All systems operational · refreshed ${utcStamp()}`;
      }
    }

    async function simulateHtmxRefresh() {
      if (busy || !button) return;
      busy = true;
      button.setAttribute("aria-busy", "true");
      button.disabled = true;
      if (trace) {
        trace.textContent = "GET /status → fragment…";
        trace.classList.add("is-visible");
      }

      const reduced =
        typeof window.matchMedia === "function" &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      await delay(reduced ? 40 : 280);

      const current = root.querySelector("#service-status");
      if (!current || !current.parentNode) {
        busy = false;
        button.removeAttribute("aria-busy");
        button.disabled = false;
        return;
      }

      // HTMX outerHTML swap of the declared region (simulated).
      const next = statusMarkup(utcStamp());
      current.replaceWith(next);
      if (!reduced) {
        void next.offsetWidth;
        next.classList.add("is-swapping");
        window.setTimeout(() => next.classList.remove("is-swapping"), 450);
      }

      // Fade hint in place — do not remove it from layout.
      hint?.classList.add("is-done");
      if (trace) {
        trace.textContent = "GET /status → 200 fragment (#service-status)";
        trace.classList.add("is-visible");
      }

      busy = false;
      button.removeAttribute("aria-busy");
      button.disabled = false;
      button.focus({ preventScroll: true });
    }

    button?.addEventListener("click", (event) => {
      event.preventDefault();
      void simulateHtmxRefresh();
    });
  }

  function boot(doc) {
    for (const root of doc.querySelectorAll("[data-hedron-hello-refresh]")) {
      initSim(root);
    }
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(() => boot(document));
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => boot(document));
  } else {
    boot(document);
  }
})();
