(function () {
  "use strict";

  function status(demo, message) {
    const node = demo.querySelector("[data-hdc-status]");
    if (node) node.textContent = message;
  }

  function trace(demo, method, path, result) {
    const node = demo.querySelector("[data-hdc-request]");
    if (!node) return;
    node.hidden = false;
    const code = node.querySelector("code");
    if (code) code.textContent = `${method} ${path} → ${result}`;
  }

  function initTabs(demo) {
    const tabs = Array.from(demo.querySelectorAll("[data-hdc-tab]"));
    const panels = Array.from(demo.querySelectorAll("[data-hdc-panel]"));
    function select(tab) {
      const selected = tab.dataset.hdcTab;
      for (const candidate of tabs) {
        const active = candidate === tab;
        candidate.setAttribute("aria-selected", String(active));
        candidate.tabIndex = active ? 0 : -1;
      }
      for (const panel of panels) panel.hidden = panel.dataset.hdcPanel !== selected;
    }
    for (const tab of tabs) {
      tab.addEventListener("click", () => select(tab));
      tab.addEventListener("keydown", (event) => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        let next = tabs.indexOf(tab);
        if (event.key === "ArrowRight") next = (next + 1) % tabs.length;
        if (event.key === "ArrowLeft") next = (next - 1 + tabs.length) % tabs.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = tabs.length - 1;
        tabs[next].focus();
        select(tabs[next]);
      });
    }
  }

  function initDemo(demo) {
    if (demo.dataset.hdcReady === "true") return;
    demo.dataset.hdcReady = "true";

    initTabs(demo);

    for (const form of demo.querySelectorAll("[data-hdc-form]")) {
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        if (typeof form.reportValidity === "function" && !form.reportValidity()) return;
        const email = new FormData(form).get("email");
        status(demo, email ? `Submitted ${email}. The docs returned a simulated success fragment.` : "Form submitted in the browser demo.");
        trace(demo, "POST", "/demo", "200 fragment");
      });
    }

    demo.querySelector("[data-hdc-file]")?.addEventListener("change", (event) => {
      const files = Array.from(event.currentTarget.files || []);
      status(demo, files.length ? `${files.map((file) => file.name).join(", ")} selected. Server validation would run on submit.` : "No file selected.");
    });

    demo.querySelector("[data-hdc-filter]")?.addEventListener("input", (event) => {
      const query = event.currentTarget.value.trim().toLocaleLowerCase();
      const rows = Array.from(demo.querySelectorAll("[data-hdc-rows] tr"));
      let shown = 0;
      for (const row of rows) {
        row.hidden = query !== "" && !row.textContent.toLocaleLowerCase().includes(query);
        if (!row.hidden) shown += 1;
      }
      status(demo, `Showing ${shown} employee${shown === 1 ? "" : "s"}.`);
    });

    for (const input of demo.querySelectorAll("[data-hdc-dirty]")) {
      input.addEventListener("input", () => status(demo, "Unsaved changes."));
    }

    for (const link of demo.querySelectorAll("[data-hdc-page]")) {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        const page = Number(link.dataset.hdcPage || 1);
        const names = [["Alpha", "Bravo", "Charlie"], ["Delta", "Echo", "Foxtrot"], ["Golf", "Hotel", "India"]][page - 1];
        const content = demo.querySelector("[data-hdc-page-content]");
        if (content) {
          content.querySelector("strong").textContent = `Results ${(page - 1) * 3 + 1}–${page * 3}`;
          content.querySelector("span").textContent = names.join(" · ");
        }
        for (const candidate of demo.querySelectorAll("[data-hdc-page]")) {
          if (candidate === link) candidate.setAttribute("aria-current", "page");
          else candidate.removeAttribute("aria-current");
        }
        trace(demo, "GET", `?page=${page}`, "200 fragment");
        content?.focus?.();
      });
    }

    demo.querySelector("[data-hdc-theme-form]")?.addEventListener("submit", (event) => {
      event.preventDefault();
      const select = demo.querySelector("[data-hdc-theme]");
      const selected = select?.value || "Light";
      const swatch = demo.querySelector("[data-hdc-theme-swatch]");
      if (swatch) swatch.dataset.previewTheme = selected.toLocaleLowerCase();
      status(demo, `${selected} preview selected. A server would persist this preference.`);
      trace(demo, "POST", "/preferences/color", "204");
    });

    demo.addEventListener("click", (event) => {
      const button = event.target.closest("[data-hdc-action]");
      if (!button || !demo.contains(button)) return;
      const action = button.dataset.hdcAction;

      if (action === "count") {
        const count = demo.querySelector("[data-hdc-count]");
        if (count) count.textContent = String(Number(count.textContent || 0) + 1);
        status(demo, "Button activated.");
      }
      if (action === "refresh") {
        button.disabled = true;
        const result = demo.querySelector("#status-card");
        if (result) result.innerHTML = "<strong>Refreshing…</strong><span>Simulated request in progress</span>";
        trace(demo, "GET", "/status", "pending");
        window.setTimeout(() => {
          if (result) result.innerHTML = `<strong>Service healthy</strong><span>Checked at ${new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'})}</span>`;
          button.disabled = false;
          trace(demo, "GET", "/status", "200 fragment");
        }, 550);
      }
      if (action === "lazy") {
        const target = demo.querySelector("[data-hdc-lazy]");
        button.disabled = true;
        trace(demo, "GET", "/activity-feed", "pending");
        window.setTimeout(() => {
          if (target) {
            target.setAttribute("aria-busy", "false");
            target.innerHTML = "<strong>3 recent events</strong><span>Deployment, approval, and release notes loaded.</span>";
          }
          trace(demo, "GET", "/activity-feed", "200 fragment");
        }, 650);
      }
      if (action === "poll") {
        button.disabled = true;
        const state = demo.querySelector("[data-hdc-poll-state]");
        const detail = demo.querySelector("[data-hdc-poll-detail]");
        const updates = [["Running", "Step 1 of 2"], ["Running", "Step 2 of 2"], ["Complete", "84 records imported; polling stopped"]];
        let index = 0;
        trace(demo, "GET", "/jobs/42", "200 Running");
        const timer = window.setInterval(() => {
          const update = updates[index++];
          if (state) state.textContent = update[0];
          if (detail) detail.textContent = update[1];
          trace(demo, "GET", "/jobs/42", `200 ${update[0]}`);
          if (index === updates.length) {
            window.clearInterval(timer);
            button.disabled = false;
            button.textContent = "Run polling demo again";
          }
        }, 700);
      }
      if (action === "more") {
        const feed = demo.querySelector("[data-hdc-feed]");
        const count = feed?.children.length || 0;
        for (const text of ["Tests passed", "Release published"]) {
          const item = document.createElement("li");
          item.textContent = text;
          feed?.append(item);
        }
        status(demo, `Added 2 events. Showing ${count + 2} events.`);
        trace(demo, "GET", `/events?after=${count}`, "200 fragment");
        if (count >= 4) {
          button.disabled = true;
          button.textContent = "All events loaded";
        }
      }
      if (action === "retry") {
        const error = demo.querySelector("[data-hdc-error]");
        button.disabled = true;
        trace(demo, "GET", "/activity", "pending");
        window.setTimeout(() => {
          if (error) error.outerHTML = '<div class="hdc-result" role="status"><strong>Activity restored</strong><span>The retry returned a successful fragment.</span></div>';
          trace(demo, "GET", "/activity", "200 fragment");
        }, 550);
      }
      if (action === "save-editor") {
        button.disabled = true;
        status(demo, "Saving 2 changed rows…");
        trace(demo, "POST", "/allocations/changes", "pending");
        window.setTimeout(() => {
          button.disabled = false;
          status(demo, "2 rows saved. Version 8 returned by the simulated server.");
          trace(demo, "POST", "/allocations/changes", "200 version=8");
        }, 550);
      }
      if (action === "show-toast") {
        const toast = demo.querySelector("[data-hdc-toast]");
        if (toast) toast.hidden = false;
      }
      if (action === "dismiss") {
        const toast = demo.querySelector("[data-hdc-toast]");
        if (toast) toast.hidden = true;
        demo.querySelector('[data-hdc-action="show-toast"]')?.focus();
      }
    });
  }

  function init(root) {
    for (const demo of root.querySelectorAll("[data-hedron-component-demo]")) initDemo(demo);
  }

  if (typeof document$ !== "undefined") document$.subscribe(() => init(document));
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => init(document));
  else init(document);
})();
