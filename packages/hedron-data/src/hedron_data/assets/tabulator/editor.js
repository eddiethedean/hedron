/**
 * Hedron DataEditor host — Tabulator-shaped Web Component adapter.
 * CSP-friendly: no inline handlers; init/dispose across HTMX swaps.
 */
(function () {
  const TAG = "hedron-data-editor";

  class HedronDataEditor extends HTMLElement {
    constructor() {
      super();
      this._pending = [];
      this._history = [];
      this._disposed = false;
    }

    connectedCallback() {
      this._disposed = false;
      this._boot();
    }

    disconnectedCallback() {
      this.dispose();
    }

    dispose() {
      this._disposed = true;
      this._pending = [];
      this.innerHTML = "";
    }

    _boot() {
      const host = this.closest("[data-hedron-module='hedron-data:tabulator-editor']") || this;
      let payload = {};
      try {
        payload = JSON.parse(host.getAttribute("data-hedron-payload") || "{}");
      } catch (_) {
        payload = {};
      }
      this._payload = payload;
      this._renderShell(payload);
      this._announce("Data editor ready. Use Tab to move between cells.");
    }

    _announce(msg) {
      let live = this.querySelector("[data-hedron-live]");
      if (!live) {
        live = document.createElement("div");
        live.setAttribute("data-hedron-live", "");
        live.setAttribute("aria-live", "polite");
        live.className = "hedron-sr-only";
        this.prepend(live);
      }
      live.textContent = msg;
    }

    _renderShell(payload) {
      const toolbar = document.createElement("div");
      toolbar.className = "hedron-data-editor-toolbar";
      toolbar.setAttribute("role", "toolbar");

      const saveBtn = document.createElement("button");
      saveBtn.type = "button";
      saveBtn.textContent = "Save";
      saveBtn.addEventListener("click", () => this._save());
      toolbar.appendChild(saveBtn);

      const undoBtn = document.createElement("button");
      undoBtn.type = "button";
      undoBtn.textContent = "Undo";
      undoBtn.addEventListener("click", () => this._undo());
      toolbar.appendChild(undoBtn);

      const exportBtn = document.createElement("button");
      exportBtn.type = "button";
      exportBtn.textContent = "Export CSV";
      exportBtn.addEventListener("click", () => this._exportCsv());
      toolbar.appendChild(exportBtn);

      const table = document.createElement("table");
      table.setAttribute("role", "grid");
      table.className = "hedron-data-editor-grid";
      const thead = document.createElement("thead");
      const hr = document.createElement("tr");
      (payload.columns || []).forEach((col) => {
        if (col.visible === false) return;
        const th = document.createElement("th");
        th.scope = "col";
        th.textContent = col.title || col.field;
        hr.appendChild(th);
      });
      thead.appendChild(hr);
      table.appendChild(thead);

      const tbody = document.createElement("tbody");
      (payload.rows || []).forEach((row) => {
        const tr = document.createElement("tr");
        tr.dataset.rowKey = String(row[payload.keyField || "id"] ?? "");
        (payload.columns || []).forEach((col) => {
          if (col.visible === false) return;
          const td = document.createElement("td");
          td.tabIndex = 0;
          td.dataset.field = col.field;
          td.textContent = row[col.field] == null ? "" : String(row[col.field]);
          if (col.editor) {
            td.contentEditable = "true";
            td.addEventListener("blur", () => {
              this._queueUpdate(tr.dataset.rowKey, col.field, td.textContent);
            });
            td.addEventListener("keydown", (ev) => {
              if (ev.key === "Enter") {
                ev.preventDefault();
                td.blur();
              }
            });
          }
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);

      this.replaceChildren(toolbar, table);
    }

    _queueUpdate(rowKey, field, value) {
      this._history.push({ rowKey, field, value });
      this._pending = this._pending.filter(
        (u) => !(u.row_key === rowKey && u.field === field)
      );
      this._pending.push({ row_key: rowKey, field, value, row_version: this._payload.version });
      this._announce(`Pending edit ${field} on row ${rowKey}`);
    }

    _undo() {
      const last = this._history.pop();
      if (!last) return;
      this._pending = this._pending.filter(
        (u) => !(u.row_key === last.rowKey && u.field === last.field)
      );
      this._announce("Undid last edit");
    }

    _exportCsv() {
      const cols = (this._payload.columns || []).filter((c) => c.visible !== false);
      const lines = [cols.map((c) => c.title || c.field).join(",")];
      (this._payload.rows || []).forEach((row) => {
        lines.push(cols.map((c) => JSON.stringify(row[c.field] ?? "")).join(","));
      });
      const blob = new Blob([lines.join("\n")], { type: "text/csv" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "export.csv";
      a.click();
      URL.revokeObjectURL(a.href);
    }

    async _save() {
      const endpoint = this._payload.saveEndpoint;
      if (!endpoint) {
        this._announce("No save endpoint configured");
        return;
      }
      const body = {
        updates: this._pending,
        inserts: [],
        deletes: [],
        dataset_version: this._payload.version,
      };
      const csrf = document.querySelector('meta[name="csrf-token"]');
      const headers = { "Content-Type": "application/json" };
      if (csrf) headers["X-CSRF-Token"] = csrf.getAttribute("content") || "";
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers,
          credentials: "same-origin",
          body: JSON.stringify(body),
        });
        const data = await res.json();
        if (data.ok) {
          this._pending = [];
          this._announce("Saved successfully");
        } else if (data.conflicts && data.conflicts.length) {
          this._announce("Conflict: choose reload, retain-and-retry, compare, or cancel");
          this.dispatchEvent(
            new CustomEvent("hedron-data-conflict", { detail: data, bubbles: true })
          );
        } else if (data.errors && data.errors.length) {
          const first = data.errors[0];
          this._announce(`Validation error: ${first.message || "invalid"}`);
          const cell = this.querySelector(
            `tr[data-row-key="${first.row_key}"] td[data-field="${first.field}"]`
          );
          if (cell) cell.focus();
        }
      } catch (err) {
        this._announce("Save failed");
      }
    }
  }

  if (!customElements.get(TAG)) {
    customElements.define(TAG, HedronDataEditor);
  }

  function enhance(root) {
    root.querySelectorAll("[data-hedron-module='hedron-data:tabulator-editor']").forEach((host) => {
      if (host.querySelector(TAG)) return;
      const el = document.createElement(TAG);
      host.appendChild(el);
    });
  }

  function disposeAll(root) {
    root.querySelectorAll(TAG).forEach((el) => el.dispose && el.dispose());
  }

  document.addEventListener("DOMContentLoaded", () => enhance(document));
  document.body && document.body.addEventListener("htmx:afterSwap", (ev) => {
    enhance(ev.target || document);
  });
  document.body && document.body.addEventListener("htmx:beforeSwap", (ev) => {
    disposeAll(ev.target || document);
  });

  window.HedronDataEditor = { enhance, disposeAll };
})();
