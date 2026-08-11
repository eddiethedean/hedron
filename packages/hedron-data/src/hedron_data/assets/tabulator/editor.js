/**
 * Hedron DataEditor host — Tabulator-shaped Web Component adapter.
 * CSP-friendly: no inline handlers; init/dispose across HTMX swaps.
 */
(function () {
  const TAG = "hedron-data-editor";

  function cssEscape(value) {
    if (window.CSS && CSS.escape) return CSS.escape(String(value));
    return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\$&");
  }

  /** Mirror hedron_data.spreadsheet._reject_or_sanitize(..., formula_policy="sanitize"). */
  function sanitizeFormulaCell(value) {
    const text = value == null ? "" : String(value);
    const dangerous =
      text.length > 0 &&
      ("=+-@".indexOf(text.charAt(0)) !== -1 || text.charAt(0) === "\t" || text.charAt(0) === "\r");
    if (!dangerous) return text;
    return "'" + text.replace(/^[\t\r]+/, "");
  }

  /** RFC 4180-style field encoding (doubled quotes; quote when needed). */
  function csvEscapeField(value) {
    const text = value == null ? "" : String(value);
    if (/[",\r\n]/.test(text)) {
      return '"' + text.replace(/"/g, '""') + '"';
    }
    return text;
  }

  /**
   * Build a CSV document from column metadata and row objects.
   * @param {{field: string, title?: string, visible?: boolean}[]} columns
   * @param {Record<string, unknown>[]} rows
   */
  function buildCsv(columns, rows) {
    const cols = (columns || []).filter((c) => c && c.visible !== false);
    const header = cols.map((c) => csvEscapeField(c.title || c.field)).join(",");
    const lines = [header];
    (rows || []).forEach((row) => {
      lines.push(
        cols
          .map((c) => csvEscapeField(sanitizeFormulaCell(row[c.field] == null ? "" : row[c.field])))
          .join(",")
      );
    });
    return lines.join("\n");
  }

  const ElementBase = typeof HTMLElement !== "undefined" ? HTMLElement : class {};

  class HedronDataEditor extends ElementBase {
    constructor() {
      super();
      this._pending = [];
      this._history = [];
      this._inserts = [];
      this._deletes = [];
      this._disposed = false;
      this._rows = [];
      this._tempId = 0;
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
      this._history = [];
      this._inserts = [];
      this._deletes = [];
      this.innerHTML = "";
    }

    _boot() {
      const host =
        this.closest("[data-hedron-module='hedron-data:tabulator-editor']") || this;
      let payload = {};
      try {
        payload = JSON.parse(host.getAttribute("data-hedron-payload") || "{}");
      } catch (_) {
        payload = {};
      }
      this._payload = payload;
      this._rows = Array.isArray(payload.rows) ? payload.rows.map((r) => ({ ...r })) : [];
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
      saveBtn.className = "hedron-button hedron-button-primary";
      saveBtn.addEventListener("click", () => this._save());
      toolbar.appendChild(saveBtn);

      const undoBtn = document.createElement("button");
      undoBtn.type = "button";
      undoBtn.textContent = "Undo";
      undoBtn.className = "hedron-button hedron-button-secondary";
      undoBtn.addEventListener("click", () => this._undo());
      toolbar.appendChild(undoBtn);

      const insertBtn = document.createElement("button");
      insertBtn.type = "button";
      insertBtn.textContent = "Insert row";
      insertBtn.className = "hedron-button hedron-button-secondary";
      insertBtn.addEventListener("click", () => this._insertRow());
      toolbar.appendChild(insertBtn);

      if (payload.allowDeletes !== false) {
        const delBtn = document.createElement("button");
        delBtn.type = "button";
        delBtn.textContent = "Delete selected";
        delBtn.className = "hedron-button hedron-button-danger";
        delBtn.addEventListener("click", () => this._deleteSelected());
        toolbar.appendChild(delBtn);
      }

      const exportBtn = document.createElement("button");
      exportBtn.type = "button";
      exportBtn.textContent = "Export CSV";
      exportBtn.className = "hedron-button hedron-button-secondary";
      exportBtn.addEventListener("click", () => this._exportCsv());
      toolbar.appendChild(exportBtn);

      const conflictBar = document.createElement("div");
      conflictBar.className = "hedron-data-editor-conflicts";
      conflictBar.hidden = true;
      conflictBar.setAttribute("data-conflict-bar", "");
      (payload.conflictActions || ["reload", "retain-and-retry", "compare", "cancel"]).forEach(
        (action) => {
          const b = document.createElement("button");
          b.type = "button";
          b.textContent = action;
          b.className = "hedron-button hedron-button-secondary";
          b.addEventListener("click", () => this._handleConflict(action));
          conflictBar.appendChild(b);
        }
      );

      const table = document.createElement("table");
      table.setAttribute("role", "grid");
      table.className = "hedron-data-editor-grid";
      const thead = document.createElement("thead");
      const hr = document.createElement("tr");
      const selTh = document.createElement("th");
      selTh.scope = "col";
      selTh.textContent = "Select";
      hr.appendChild(selTh);
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
      tbody.setAttribute("data-editor-body", "");
      this._rows.forEach((row) => tbody.appendChild(this._rowElement(row, payload)));
      table.appendChild(tbody);

      this.replaceChildren(toolbar, conflictBar, table);
    }

    _rowElement(row, payload) {
      const tr = document.createElement("tr");
      const key = String(row[payload.keyField || "id"] ?? "");
      tr.dataset.rowKey = key;
      const selTd = document.createElement("td");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.setAttribute("aria-label", "Select row " + key);
      selTd.appendChild(cb);
      tr.appendChild(selTd);
      (payload.columns || []).forEach((col) => {
        if (col.visible === false) return;
        const td = document.createElement("td");
        td.tabIndex = 0;
        td.dataset.field = col.field;
        const value = row[col.field];
        if (col.editor === "boolean") {
          const input = document.createElement("input");
          input.type = "checkbox";
          input.checked = Boolean(value);
          input.disabled = !col.editor;
          input.addEventListener("change", () => {
            this._queueUpdate(key, col.field, input.checked, String(value));
            if ((payload.saveMode || "batch") === "cell") this._save();
          });
          td.appendChild(input);
        } else if (col.choices && col.choices.length) {
          const select = document.createElement("select");
          col.choices.forEach((choice) => {
            const opt = document.createElement("option");
            opt.value = String(choice);
            opt.textContent = String(choice);
            if (String(choice) === String(value ?? "")) opt.selected = true;
            select.appendChild(opt);
          });
          select.disabled = col.editor === false;
          select.addEventListener("change", () => {
            this._queueUpdate(key, col.field, select.value, String(value ?? ""));
            if ((payload.saveMode || "batch") === "cell") this._save();
          });
          td.appendChild(select);
        } else {
          td.textContent = value == null ? "" : String(value);
          if (col.editor) {
            td.contentEditable = "true";
            td.addEventListener("focus", () => {
              td.dataset.original = td.textContent || "";
              td.dataset.editCancel = "0";
            });
            td.addEventListener("blur", () => {
              if (td.dataset.editCancel === "1") {
                td.dataset.editCancel = "0";
                return;
              }
              this._queueUpdate(key, col.field, td.textContent, td.dataset.original || "");
              if ((payload.saveMode || "batch") === "cell") this._save();
            });
            td.addEventListener("keydown", (ev) => {
              if (ev.key === "Enter") {
                ev.preventDefault();
                td.blur();
                if ((payload.saveMode || "batch") === "row") this._save();
              } else if (ev.key === "Escape") {
                ev.preventDefault();
                td.dataset.editCancel = "1";
                td.textContent = td.dataset.original || "";
                td.blur();
              }
            });
          }
        }
        tr.appendChild(td);
      });
      return tr;
    }

    _queueUpdate(rowKey, field, value, previous) {
      this._history.push({
        kind: "update",
        rowKey,
        field,
        value,
        previous: previous == null ? "" : String(previous),
      });
      this._pending = this._pending.filter(
        (u) => !(u.row_key === rowKey && u.field === field)
      );
      this._pending.push({
        row_key: rowKey,
        field,
        value,
        row_version: this._payload.version,
      });
      const keyField = this._payload.keyField || "id";
      const row = this._rows.find((r) => String(r[keyField]) === String(rowKey));
      if (row) row[field] = value;
      this._announce("Pending edit " + field + " on row " + rowKey);
    }

    _insertRow() {
      this._tempId += 1;
      const key = "new-" + this._tempId;
      const row = { [this._payload.keyField || "id"]: key };
      (this._payload.columns || []).forEach((col) => {
        if (col.field !== (this._payload.keyField || "id")) row[col.field] = "";
      });
      this._rows.push(row);
      this._inserts.push(row);
      this._history.push({ kind: "insert", rowKey: key, row });
      const body = this.querySelector("[data-editor-body]");
      if (body) body.appendChild(this._rowElement(row, this._payload));
      this._announce("Inserted row " + key);
      if ((this._payload.saveMode || "batch") === "row") this._save();
    }

    _deleteSelected() {
      const body = this.querySelector("[data-editor-body]");
      if (!body) return;
      Array.from(body.querySelectorAll("tr")).forEach((tr) => {
        const cb = tr.querySelector('input[type="checkbox"]');
        if (!cb || !cb.checked) return;
        const key = tr.dataset.rowKey;
        this._deletes.push(key);
        this._pending = this._pending.filter((u) => u.row_key !== key);
        this._inserts = this._inserts.filter(
          (r) => String(r[this._payload.keyField || "id"]) !== key
        );
        const rowSnapshot = { ...(this._rows.find(
          (r) => String(r[this._payload.keyField || "id"]) === key
        ) || {}) };
        this._rows = this._rows.filter(
          (r) => String(r[this._payload.keyField || "id"]) !== key
        );
        this._history.push({ kind: "delete", rowKey: key, row: rowSnapshot });
        tr.remove();
      });
      this._announce("Deleted selected rows");
      if ((this._payload.saveMode || "batch") === "row") this._save();
    }

    _undo() {
      const last = this._history.pop();
      if (!last) return;
      if (last.kind === "update") {
        this._pending = this._pending.filter(
          (u) => !(u.row_key === last.rowKey && u.field === last.field)
        );
        const keyField = this._payload.keyField || "id";
        const row = this._rows.find((r) => String(r[keyField]) === String(last.rowKey));
        const cell = this.querySelector(
          'tr[data-row-key="' +
            cssEscape(last.rowKey) +
            '"] td[data-field="' +
            cssEscape(last.field) +
            '"]'
        );
        if (cell) {
          const input = cell.querySelector("input,select");
          if (input && input.type === "checkbox") {
            input.checked = last.previous === "true";
            if (row) row[last.field] = last.previous === "true";
          } else if (input) {
            input.value = last.previous;
            if (row) row[last.field] = last.previous;
          } else {
            cell.textContent = last.previous;
            if (row) row[last.field] = last.previous;
          }
        } else if (row) {
          row[last.field] = last.previous;
        }
      } else if (last.kind === "insert") {
        this._inserts = this._inserts.filter(
          (r) => String(r[this._payload.keyField || "id"]) !== last.rowKey
        );
        this._rows = this._rows.filter(
          (r) => String(r[this._payload.keyField || "id"]) !== last.rowKey
        );
        const tr = this.querySelector('tr[data-row-key="' + cssEscape(last.rowKey) + '"]');
        if (tr) tr.remove();
      } else if (last.kind === "delete") {
        this._deletes = this._deletes.filter((k) => k !== last.rowKey);
        const body = this.querySelector("[data-editor-body]");
        if (body && last.row) {
          this._rows.push({ ...last.row });
          body.appendChild(this._rowElement(last.row, this._payload));
        }
      }
      this._announce("Undid last edit");
    }

    _exportCsv() {
      const csv = buildCsv(this._payload.columns || [], this._rows);
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "export.csv";
      a.click();
      URL.revokeObjectURL(a.href);
    }

    _handleConflict(action) {
      const bar = this.querySelector("[data-conflict-bar]");
      if (action === "reload") {
        window.location.reload();
        return;
      }
      if (action === "cancel") {
        this._pending = [];
        if (bar) bar.hidden = true;
        this._announce("Cancelled pending conflicted edits");
        return;
      }
      if (action === "retain-and-retry") {
        if (bar) bar.hidden = true;
        this._save();
        return;
      }
      if (action === "compare") {
        this._announce("Compare server and client values, then choose retry or cancel");
      }
    }

    async _save() {
      const endpoint = this._payload.saveEndpoint;
      if (!endpoint) {
        this._announce("No save endpoint configured");
        return;
      }
      const body = {
        updates: this._pending,
        inserts: this._inserts,
        deletes: this._deletes,
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
        if (res.status === 403) {
          this._announce("Save forbidden (CSRF or authorization)");
          return;
        }
        let data;
        try {
          data = await res.json();
        } catch (parseErr) {
          this._announce("Save failed");
          return;
        }
        const bar = this.querySelector("[data-conflict-bar]");
        if (data.ok) {
          this._pending = [];
          this._inserts = [];
          this._deletes = [];
          if (bar) bar.hidden = true;
          if (data.version) this._payload.version = data.version;
          this._announce("Saved successfully");
        } else if (data.conflicts && data.conflicts.length) {
          this._announce("Conflict: choose reload, retain-and-retry, compare, or cancel");
          if (bar) bar.hidden = false;
          this.dispatchEvent(
            new CustomEvent("hedron-data-conflict", { detail: data, bubbles: true })
          );
        } else if (data.errors && data.errors.length) {
          const first = data.errors[0];
          this._announce("Validation error: " + (first.message || "invalid"));
          const cell = this.querySelector(
            'tr[data-row-key="' +
              cssEscape(first.row_key || "") +
              '"] td[data-field="' +
              cssEscape(first.field || "") +
              '"]'
          );
          if (cell) cell.focus();
        } else {
          this._announce("Save failed");
        }
      } catch (err) {
        this._announce("Save failed");
      }
    }
  }

  if (typeof customElements !== "undefined" && !customElements.get(TAG)) {
    customElements.define(TAG, HedronDataEditor);
  }

  function enhance(root) {
    root
      .querySelectorAll("[data-hedron-module='hedron-data:tabulator-editor']")
      .forEach((host) => {
        if (host.querySelector(TAG)) return;
        const el = document.createElement(TAG);
        host.appendChild(el);
        const fallback = host.querySelector(":scope > .hedron-data-editor-fallback");
        if (fallback) fallback.hidden = true;
      });
  }

  function disposeAll(root) {
    root.querySelectorAll(TAG).forEach((el) => el.dispose && el.dispose());
  }

  const api = {
    enhance,
    disposeAll,
    sanitizeFormulaCell,
    csvEscapeField,
    buildCsv,
  };

  if (typeof document !== "undefined" && document.addEventListener) {
    document.addEventListener("DOMContentLoaded", () => enhance(document));
    document.addEventListener("htmx:afterSwap", (ev) => {
      enhance(ev.target || document);
    });
    document.addEventListener("htmx:beforeSwap", (ev) => {
      disposeAll(ev.target || document);
    });
  }

  if (typeof window !== "undefined") {
    window.HedronDataEditor = api;
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})();
