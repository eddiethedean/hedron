(function () {
  "use strict";

  function initials(name) {
    return name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() || "")
      .join("");
  }

  function initTeamDemo(demo) {
    if (demo.dataset.demoReady === "true") return;
    demo.dataset.demoReady = "true";

    const dialog = demo.querySelector("[data-demo-dialog]");
    const form = demo.querySelector("[data-demo-form]");
    const rows = demo.querySelector("[data-demo-rows]");
    const filter = demo.querySelector("[data-demo-filter]");
    const empty = demo.querySelector("[data-demo-empty]");
    const count = demo.querySelector("[data-demo-count]");
    const status = demo.querySelector("[data-demo-status]");

    function visibleRows() {
      return Array.from(rows?.querySelectorAll("tr") || []).filter((row) => !row.hidden);
    }

    function applyFilter() {
      const query = filter.value.trim().toLocaleLowerCase();
      for (const row of rows.querySelectorAll("tr")) {
        row.hidden = query !== "" && !row.textContent.toLocaleLowerCase().includes(query);
      }
      empty.hidden = visibleRows().length !== 0;
    }

    demo.querySelector("[data-demo-open]")?.addEventListener("click", () => {
      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialog.setAttribute("open", "");
    });

    for (const close of demo.querySelectorAll("[data-demo-close]")) {
      close.addEventListener("click", () => {
        if (typeof dialog.close === "function") dialog.close();
        else dialog.removeAttribute("open");
      });
    }

    filter?.addEventListener("input", applyFilter);

    form?.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;

      const data = new FormData(form);
      const name = String(data.get("name") || "").trim();
      const email = String(data.get("email") || "").trim();
      const role = String(data.get("role") || "Member");
      const row = document.createElement("tr");

      const memberCell = document.createElement("td");
      const avatar = document.createElement("span");
      avatar.className = "hedron-avatar hedron-avatar--teal";
      avatar.textContent = initials(name);
      const memberName = document.createElement("strong");
      memberName.textContent = name;
      memberCell.append(avatar, memberName);

      const emailCell = document.createElement("td");
      emailCell.textContent = email;
      const roleCell = document.createElement("td");
      const roleBadge = document.createElement("span");
      roleBadge.className = role === "Admin" ? "hedron-role" : "hedron-role hedron-role--muted";
      roleBadge.textContent = role;
      roleCell.append(roleBadge);
      const statusCell = document.createElement("td");
      const statusBadge = document.createElement("span");
      statusBadge.className = "hedron-status";
      statusBadge.textContent = "Active";
      statusCell.append(statusBadge);

      row.append(memberCell, emailCell, roleCell, statusCell);
      rows.append(row);
      count.textContent = String(rows.querySelectorAll("tr").length);
      form.reset();
      filter.value = "";
      applyFilter();
      status.textContent = `${name} was added to the demo team.`;
      if (typeof dialog.close === "function") dialog.close();
      else dialog.removeAttribute("open");
    });
  }

  function initExplorerDemo(demo) {
    if (demo.dataset.demoReady === "true") return;
    demo.dataset.demoReady = "true";
    const tabs = Array.from(demo.querySelectorAll("[data-demo-tab]"));
    const panels = Array.from(demo.querySelectorAll("[data-demo-panel]"));

    for (const tab of tabs) {
      tab.addEventListener("click", () => {
        const selected = tab.dataset.demoTab;
        for (const candidate of tabs) {
          candidate.setAttribute("aria-selected", String(candidate === tab));
          candidate.setAttribute("tabindex", candidate === tab ? "0" : "-1");
        }
        for (const panel of panels) {
          panel.hidden = panel.dataset.demoPanel !== selected;
        }
      });

      tab.addEventListener("keydown", (event) => {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        const offset = event.key === "ArrowRight" ? 1 : -1;
        const next = tabs[(tabs.indexOf(tab) + offset + tabs.length) % tabs.length];
        next.focus();
        next.click();
      });
    }
  }

  function initExamples(root) {
    for (const demo of root.querySelectorAll('[data-hedron-demo="team-admin"]')) {
      initTeamDemo(demo);
    }
    for (const demo of root.querySelectorAll('[data-hedron-demo="explorer"]')) {
      initExplorerDemo(demo);
    }
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(() => initExamples(document));
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initExamples(document));
  } else {
    initExamples(document);
  }
})();
