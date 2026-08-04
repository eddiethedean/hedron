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

  const EXPLORER_COMPONENTS = {
    UserCard: {
      title: "UserCard",
      stability: "Beta",
      address: "localhost:8000/hedron-explorer/components/UserCard",
      path: "/components/user-card",
      mode: "FRAGMENT",
      nodes: "6",
      diagnostics: "0",
      headers: "HX-Request: true\nHX-Target: #team-list\nAccept: text/html",
      note: "Returns a fragment, applies private caching, and exposes no source path.",
      preview:
        '<article><span class="hedron-avatar hedron-avatar--violet">AL</span><div><strong>Ada Lovelace</strong><p>Platform administrator</p></div><span class="hedron-status">Active</span></article>',
      props: [
        ["name", "str", "Yes"],
        ["role", "str", "Yes"],
        ["active", "bool", "No"],
      ],
    },
    StatusBanner: {
      title: "StatusBanner",
      stability: "Beta",
      address: "localhost:8000/hedron-explorer/components/StatusBanner",
      path: "/components/status-banner",
      mode: "FRAGMENT",
      nodes: "4",
      diagnostics: "0",
      headers: "HX-Request: true\nHX-Target: #status-slot\nAccept: text/html",
      note: "Renders a scoped status strip; tone prop maps to semantic CSS variables.",
      preview:
        '<div class="hedron-preview-banner" role="status"><strong>Phase 0.10 ready</strong><span>Live interaction Supported on the FastAPI flagship.</span></div>',
      props: [
        ["label", "str", "Yes"],
        ["tone", "Literal['info','success','warning']", "No"],
      ],
    },
    TeamTable: {
      title: "TeamTable",
      stability: "Beta",
      address: "localhost:8000/hedron-explorer/components/TeamTable",
      path: "/components/team-table",
      mode: "FRAGMENT",
      nodes: "18",
      diagnostics: "0",
      headers: "HX-Request: true\nHX-Target: #people-panel\nAccept: text/html",
      note: "Returns a table fragment for the people panel; filter state stays on the host page.",
      preview:
        '<table class="hedron-preview-table"><thead><tr><th>Member</th><th>Role</th></tr></thead><tbody><tr><td>Ada Lovelace</td><td>Admin</td></tr><tr><td>Grace Hopper</td><td>Member</td></tr></tbody></table>',
      props: [
        ["rows", "Sequence[TeamRow]", "Yes"],
        ["caption", "str", "No"],
      ],
    },
  };

  function initExplorerDemo(demo) {
    if (demo.dataset.demoReady === "true") return;
    demo.dataset.demoReady = "true";
    const tabs = Array.from(demo.querySelectorAll("[data-demo-tab]"));
    const panels = Array.from(demo.querySelectorAll("[data-demo-panel]"));
    const items = Array.from(demo.querySelectorAll("[data-demo-component]"));
    const mobileSelect = demo.querySelector("[data-demo-component-select]");

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

    function selectComponent(name) {
      const catalog = EXPLORER_COMPONENTS[name];
      if (!catalog) return;

      for (const item of items) {
        const active = item.dataset.demoComponent === name;
        item.classList.toggle("is-selected", active);
        if (active) item.setAttribute("aria-current", "true");
        else item.removeAttribute("aria-current");
      }
      if (mobileSelect) mobileSelect.value = name;

      const address = demo.querySelector("[data-demo-address]");
      const title = demo.querySelector("[data-demo-title]");
      const stability = demo.querySelector("[data-demo-stability]");
      const preview = demo.querySelector("[data-demo-preview]");
      const propsBody = demo.querySelector("[data-demo-props]");
      const path = demo.querySelector("[data-demo-path]");
      const headers = demo.querySelector("[data-demo-headers]");
      const note = demo.querySelector("[data-demo-request-note]");
      const mode = demo.querySelector("[data-demo-fact-mode]");
      const nodes = demo.querySelector("[data-demo-fact-nodes]");
      const diagnostics = demo.querySelector("[data-demo-fact-diagnostics]");

      if (address) address.textContent = catalog.address;
      if (title) title.textContent = catalog.title;
      if (stability) stability.textContent = catalog.stability;
      if (preview) preview.innerHTML = catalog.preview;
      if (path) path.textContent = catalog.path;
      if (headers) headers.textContent = catalog.headers;
      if (note) note.textContent = catalog.note;
      if (mode) mode.textContent = catalog.mode;
      if (nodes) nodes.textContent = catalog.nodes;
      if (diagnostics) diagnostics.textContent = catalog.diagnostics;

      if (propsBody) {
        propsBody.replaceChildren();
        for (const [prop, type, required] of catalog.props) {
          const row = document.createElement("tr");
          const propCell = document.createElement("td");
          const propCode = document.createElement("code");
          propCode.textContent = prop;
          propCell.append(propCode);
          const typeCell = document.createElement("td");
          const typeCode = document.createElement("code");
          typeCode.textContent = type;
          typeCell.append(typeCode);
          const requiredCell = document.createElement("td");
          requiredCell.textContent = required;
          row.append(propCell, typeCell, requiredCell);
          propsBody.append(row);
        }
      }
    }

    for (const item of items) {
      item.addEventListener("click", () => selectComponent(item.dataset.demoComponent));
      item.addEventListener("keydown", (event) => {
        if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
        event.preventDefault();
        const offset = event.key === "ArrowDown" ? 1 : -1;
        const next = items[(items.indexOf(item) + offset + items.length) % items.length];
        next.focus();
        selectComponent(next.dataset.demoComponent);
      });
    }
    mobileSelect?.addEventListener("change", () => selectComponent(mobileSelect.value));
    selectComponent("UserCard");
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
