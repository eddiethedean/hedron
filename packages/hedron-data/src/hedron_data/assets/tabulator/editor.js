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
  function stripFormulaEvasionPrefix(text) {
    let index = 0;
    while (index < text.length) {
      const code = text.charCodeAt(index);
      const char = text.charAt(index);
      // BOM, ASCII controls (incl. DEL), Unicode whitespace, and Cf format chars (#191).
      const isFormat =
        (code >= 0x200b && code <= 0x200f) ||
        (code >= 0x202a && code <= 0x202e) ||
        (code >= 0x2060 && code <= 0x2064) ||
        code === 0xfeff;
      if (char === "\ufeff" || code < 32 || code === 127 || /\s/u.test(char) || isFormat) {
        index += 1;
        continue;
      }
      break;
    }
    return text.slice(index);
  }

  function sanitizeFormulaCell(value) {
    const text = value == null ? "" : String(value);
    const normalized = stripFormulaEvasionPrefix(text);
    const prefix = normalized.charAt(0);
    const dangerous =
      normalized.length > 0 &&
      ("=+-@|".indexOf(prefix) !== -1 ||
        prefix === "\uff1d" ||
        prefix === "\uff0b" ||
        prefix === "\uff0d" ||
        prefix === "\uff20" ||
        prefix === "\uff5c");
    if (!dangerous) return text;
    return "'" + normalized;
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

  function stripOpId(item) {
    if (!item || typeof item !== "object") return item;
    const copy = { ...item };
    delete copy._opId;
    return copy;
  }

  const CSRF_COOKIE_NAMES = ["hedron_csrf", "csrftoken"];

  function readCookie(name, cookieSource) {
    const raw =
      cookieSource == null
        ? typeof document !== "undefined"
          ? document.cookie || ""
          : ""
        : String(cookieSource);
    const prefix = name + "=";
    const parts = raw.split(";");
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i].trim();
      if (part.indexOf(prefix) === 0) {
        const value = part.slice(prefix.length);
        try {
          return decodeURIComponent(value);
        } catch (err) {
          return value;
        }
      }
    }
    return "";
  }

  /**
   * CSRF token for JSON fetch saves under Hedron double-submit (#216).
   * Prefer meta[name=csrf-token] when present; otherwise read a non-HttpOnly
   * cookie (hedron_csrf on FastAPI/Flask, csrftoken on Django).
   */
  function readCsrfToken(doc, cookieSource) {
    const root = doc || (typeof document !== "undefined" ? document : null);
    if (root && typeof root.querySelector === "function") {
      const meta = root.querySelector('meta[name="csrf-token"]');
      const fromMeta =
        meta && typeof meta.getAttribute === "function" ? meta.getAttribute("content") || "" : "";
      if (fromMeta) return fromMeta;
    }
    for (let i = 0; i < CSRF_COOKIE_NAMES.length; i++) {
      const fromCookie = readCookie(CSRF_COOKIE_NAMES[i], cookieSource);
      if (fromCookie) return fromCookie;
    }
    return "";
  }

  /** Snapshot live queues before fetch so success can drop only that batch. */
  function snapshotSaveBatch(pending, inserts, deletes, keyField) {
    return {
      updates: (pending || []).slice(),
      inserts: (inserts || []).slice(),
      deletes: (deletes || []).slice(),
      updateIds: (pending || []).map((u) => u._opId),
      insertIds: (inserts || []).map((r) => r._opId),
      deleteIds: (deletes || []).map((d) => (typeof d === "string" ? d : d._opId)),
      keyField: keyField || "id",
    };
  }

  /**
   * Mirror InMemoryDataSource: each accepted *row* (unique key among updates)
   * plus each insert bumps the shared counter once (#113).
   */
  function rowVersionsAfterBatch(snapshot, nextVersion) {
    const updates = snapshot.updates || [];
    const inserts = snapshot.inserts || [];
    const touchedRows = [];
    const seen = new Set();
    updates.forEach((u) => {
      const key = String(u.row_key);
      if (!seen.has(key)) {
        seen.add(key);
        touchedRows.push(key);
      }
    });
    const bumps = touchedRows.length + inserts.length;
    if (!bumps || nextVersion == null || nextVersion === "") return {};
    const end = Number(nextVersion);
    if (!Number.isFinite(end)) return {};
    let counter = end - bumps;
    const versions = {};
    const keyField = snapshot.keyField || "id";
    touchedRows.forEach((key) => {
      counter += 1;
      versions[key] = String(counter);
    });
    inserts.forEach((row) => {
      counter += 1;
      if (row && row[keyField] != null) versions[String(row[keyField])] = String(counter);
    });
    return versions;
  }

  /** Remove only operations that were included in the submitted snapshot. */
  function reconcileAfterSuccess(pending, inserts, deletes, snapshot, nextVersion) {
    const updateIds = new Set(snapshot.updateIds || []);
    const insertIds = new Set(snapshot.insertIds || []);
    const deleteIds = new Set(snapshot.deleteIds || []);
    const touchedVersions = rowVersionsAfterBatch(snapshot, nextVersion);
    return {
      pending: (pending || [])
        .filter((u) => !updateIds.has(u._opId))
        .map((u) => {
          if (u.row_version == null) return u;
          const next = touchedVersions[String(u.row_key)];
          if (next == null) return u;
          return { ...u, row_version: next };
        }),
      inserts: (inserts || []).filter((r) => !insertIds.has(r._opId)),
      deletes: (deletes || []).filter((d) => {
        const id = typeof d === "string" ? d : d._opId;
        return !deleteIds.has(id);
      }),
    };
  }

  function serializeSaveBody(pending, inserts, deletes, version) {
    return {
      updates: (pending || []).map(stripOpId),
      inserts: (inserts || []).map(stripOpId),
      deletes: (deletes || []).map((d) => (typeof d === "string" ? d : d.row_key)),
      dataset_version: version,
    };
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
      this._baselines = {};
      this._rowVersions = {};
      this._tempId = 0;
      this._opSeq = 0;
      this._saving = false;
      this._saveAgain = false;
      this._lastConflict = null;
      this._abort = null;
      this._optimisticState = "canonical";
      this._idempotencyKey = null;
      this._conflictServerVersion = null;
      this._booted = false;
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
      if (this._abort) {
        try { this._abort.abort(); } catch (_) {}
        this._abort = null;
      }
      this._pending = [];
      this._history = [];
      this._inserts = [];
      this._deletes = [];
      this._saving = false;
      this._saveAgain = false;
      this._optimisticState = "canonical";
      this._idempotencyKey = null;
      this._conflictServerVersion = null;
      this._booted = false;
      // Preserve SSR fallback table; remove only upgraded chrome.
      Array.from(this.children).forEach((child) => {
        if (child.classList && child.classList.contains("hedron-data-editor-fallback")) return;
        child.remove();
      });
    }

    _nextOpId() {
      this._opSeq += 1;
      return this._opSeq;
    }

    _rowVersionFor(rowKey) {
      const key = String(rowKey);
      if (this._rowVersions && this._rowVersions[key] != null) {
        return String(this._rowVersions[key]);
      }
      if (this._payload && this._payload.version != null) {
        return String(this._payload.version);
      }
      return "1";
    }

    _boot() {
      if (this._booted || this._disposed) return;
      this._booted = true;
      const host =
        this.matches("[data-hedron-element='hedron-data-editor'],[data-hedron-module='hedron-data:tabulator-editor']")
          ? this
          : this.closest("[data-hedron-module='hedron-data:tabulator-editor']") || this;
      let payload = {};
      try {
        payload = JSON.parse(host.getAttribute("data-hedron-payload") || this.getAttribute("data-hedron-payload") || "{}");
      } catch (_) {
        payload = {};
      }
      this._payload = payload;
      this._rows = Array.isArray(payload.rows) ? payload.rows.map((r) => ({ ...r })) : [];
      this._baselines = {};
      this._rowVersions = {};
      const keyField = payload.keyField || "id";
      const version = payload.version != null ? String(payload.version) : "1";
      (this._rows || []).forEach((row) => {
        const rk = String(row[keyField]);
        this._rowVersions[rk] = version;
      });
      // Keep SSR fallback in-tree; mark upgraded without HTML hidden removal of content.
      const fallback = this.querySelector(":scope > .hedron-data-editor-fallback");
      if (fallback) {
        fallback.setAttribute("data-hedron-fallback", "upgraded");
        fallback.setAttribute("aria-hidden", "true");
      }
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
      cb.addEventListener("change", () => this._emitSelection());
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
            const keyField = payload.keyField || "id";
            const live = this._rows.find((r) => String(r[keyField]) === String(key));
            const prev = live ? live[col.field] : value;
            this._queueUpdate(key, col.field, input.checked, String(prev));
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
            const keyField = payload.keyField || "id";
            const live = this._rows.find((r) => String(r[keyField]) === String(key));
            const prev = live ? live[col.field] : value;
            this._queueUpdate(key, col.field, select.value, String(prev ?? ""));
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
      const priorPending = this._pending.find(
        (u) => u.row_key === rowKey && u.field === field
      );
      this._history.push({
        kind: "update",
        rowKey,
        field,
        value,
        previous: previous == null ? "" : String(previous),
        priorPending: priorPending
          ? {
              row_key: priorPending.row_key,
              field: priorPending.field,
              value: priorPending.value,
              row_version: priorPending.row_version,
            }
          : null,
      });
      this._pending = this._pending.filter(
        (u) => !(u.row_key === rowKey && u.field === field)
      );
      this._pending.push({
        row_key: rowKey,
        field,
        value,
        row_version: this._rowVersionFor(rowKey),
        _opId: this._nextOpId(),
      });
      const keyField = this._payload.keyField || "id";
      const row = this._rows.find((r) => String(r[keyField]) === String(rowKey));
      if (row) row[field] = value;
      this._setOptimistic("proposed");
      this._announce("Pending edit " + field + " on row " + rowKey);
      this._emit("hedron-data-cell-edit", { row_key: rowKey, field, value });
    }

    _insertRow() {
      this._tempId += 1;
      const key = "new-" + this._tempId;
      const row = { [this._payload.keyField || "id"]: key, _opId: this._nextOpId() };
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
      const keyField = this._payload.keyField || "id";
      Array.from(body.querySelectorAll("tr")).forEach((tr) => {
        const cb = tr.querySelector('input[type="checkbox"]');
        if (!cb || !cb.checked) return;
        const key = tr.dataset.rowKey;
        // #119: unsaved local inserts must not become server deletes.
        const wasInsert = this._inserts.some((r) => String(r[keyField]) === String(key));
        this._pending = this._pending.filter((u) => u.row_key !== key);
        this._inserts = this._inserts.filter((r) => String(r[keyField]) !== String(key));
        if (!wasInsert) {
          this._deletes.push({ row_key: key, _opId: this._nextOpId() });
        }
        const rowSnapshot = { ...(this._rows.find((r) => String(r[keyField]) === String(key)) || {}) };
        this._rows = this._rows.filter((r) => String(r[keyField]) !== String(key));
        this._history.push({ kind: "delete", rowKey: key, row: rowSnapshot, wasInsert });
        tr.remove();
      });
      this._announce("Deleted selected rows");
      this._emit("hedron-data-row-edit", { kind: "delete" });
      if ((this._payload.saveMode || "batch") === "row") this._save();
    }

    _undo() {
      const last = this._history.pop();
      if (!last) return;
      if (last.kind === "update") {
        // #120: restore the prior pending value for this cell when undoing.
        this._pending = this._pending.filter(
          (u) => !(u.row_key === last.rowKey && u.field === last.field)
        );
        if (last.priorPending) {
          this._pending.push({ ...last.priorPending, _opId: this._nextOpId() });
        }
        const keyField = this._payload.keyField || "id";
        const row = this._rows.find((r) => String(r[keyField]) === String(last.rowKey));
        const restoreValue = last.priorPending
          ? last.priorPending.value
          : last.previous;
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
            input.checked = restoreValue === true || restoreValue === "true";
            if (row) row[last.field] = restoreValue === true || restoreValue === "true";
          } else if (input) {
            input.value = restoreValue == null ? "" : String(restoreValue);
            if (row) row[last.field] = restoreValue;
          } else {
            cell.textContent = restoreValue == null ? "" : String(restoreValue);
            if (row) row[last.field] = restoreValue;
          }
        } else if (row) {
          row[last.field] = restoreValue;
        }
        this._setOptimistic("proposed");
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
        this._deletes = this._deletes.filter((d) => {
          const key = typeof d === "string" ? d : d.row_key;
          return key !== last.rowKey;
        });
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
        this._conflictServerVersion = null;
        this._setOptimistic("rolled_back");
        if (bar) bar.hidden = true;
        this._announce("Cancelled pending conflicted edits");
        return;
      }
      if (action === "retain-and-retry") {
        // #121: rebase onto server revision from conflict; never resubmit stale base.
        if (this._conflictServerVersion != null && this._conflictServerVersion !== "") {
          this._payload.version = this._conflictServerVersion;
          const fresh = String(this._conflictServerVersion);
          this._pending = this._pending.map((u) => ({
            ...u,
            row_version: fresh,
          }));
          Object.keys(this._rowVersions || {}).forEach((rk) => {
            this._rowVersions[rk] = fresh;
          });
        } else {
          this._announce("Cannot retry without a fresh server revision; reload or cancel");
          return;
        }
        this._idempotencyKey = null;
        if (bar) bar.hidden = true;
        this._setOptimistic("proposed");
        this._save();
        return;
      }
      if (action === "compare") {
        this._announce("Compare server and client values, then choose retry or cancel");
      }
    }

    _emit(name, detail) {
      this.dispatchEvent(
        new CustomEvent(name, {
          detail: detail || {},
          bubbles: true,
          composed: true,
        })
      );
    }

    _setOptimistic(state) {
      this._optimisticState = state;
      this.setAttribute("data-hedron-optimistic", state);
      this._emit("hedron-data-optimistic", {
        state,
        base_revision: this._payload ? this._payload.version : null,
        idempotency_key: this._idempotencyKey,
      });
    }

    _selectionKeys() {
      const body = this.querySelector("[data-editor-body]");
      if (!body) return [];
      return Array.from(body.querySelectorAll("tr"))
        .filter((tr) => {
          const cb = tr.querySelector('input[type="checkbox"]');
          return cb && cb.checked;
        })
        .map((tr) => tr.dataset.rowKey);
    }

    _emitSelection() {
      const keys = this._selectionKeys();
      this._emit("hedron-data-selection-change", { keys, filters: { id: keys } });
    }

    async _save() {
      const endpoint = this._payload.saveEndpoint;
      if (!endpoint) {
        this._announce("No save endpoint configured");
        return;
      }
      if (this._saving) {
        this._saveAgain = true;
        return;
      }
      if (!this._pending.length && !this._inserts.length && !this._deletes.length) {
        return;
      }
      this._saving = true;
      this._saveAgain = false;
      if (!this._idempotencyKey) {
        this._idempotencyKey =
          "hed-opt-" + String(Date.now()) + "-" + String(this._nextOpId());
      }
      this._setOptimistic("submitted");
      const snapshot = snapshotSaveBatch(
        this._pending,
        this._inserts,
        this._deletes,
        this._payload.keyField || "id"
      );
      const body = serializeSaveBody(
        snapshot.updates,
        snapshot.inserts,
        snapshot.deletes,
        this._payload.version
      );
      body.idempotency_key = this._idempotencyKey;
      body.base_revision = this._payload.version;
      const headers = { "Content-Type": "application/json" };
      const csrfToken = readCsrfToken(document);
      if (csrfToken) headers["X-CSRF-Token"] = csrfToken;
      if (this._abort) {
        try { this._abort.abort(); } catch (_) {}
      }
      this._abort = typeof AbortController !== "undefined" ? new AbortController() : null;
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers,
          credentials: "same-origin",
          body: JSON.stringify(body),
          signal: this._abort ? this._abort.signal : undefined,
        });
        if (this._disposed) return;
        if (res.status === 403) {
          this._setOptimistic("rejected");
          this._announce("Save forbidden (CSRF or authorization)");
          return;
        }
        let data;
        try {
          data = await res.json();
        } catch (parseErr) {
          this._setOptimistic("rejected");
          this._announce("Save failed");
          return;
        }
        const bar = this.querySelector("[data-conflict-bar]");
        if (data.ok) {
          if (data.version) this._payload.version = data.version;
          const kept = reconcileAfterSuccess(
            this._pending,
            this._inserts,
            this._deletes,
            snapshot,
            this._payload.version
          );
          this._pending = kept.pending;
          this._inserts = kept.inserts;
          this._deletes = kept.deletes;
          const touched = rowVersionsAfterBatch(snapshot, this._payload.version);
          Object.keys(touched).forEach((rk) => {
            this._rowVersions[rk] = touched[rk];
          });
          this._idempotencyKey = null;
          this._conflictServerVersion = null;
          this._setOptimistic("confirmed");
          if (bar) bar.hidden = true;
          this._announce("Saved successfully");
        } else if (data.conflicts && data.conflicts.length) {
          this._conflictServerVersion =
            data.version != null && data.version !== ""
              ? data.version
              : data.server_version != null
                ? data.server_version
                : null;
          this._setOptimistic("conflicted");
          this._announce("Conflict: choose reload, retain-and-retry, compare, or cancel");
          if (bar) bar.hidden = false;
          this._emit("hedron-data-conflict", data);
        } else if (data.errors && data.errors.length) {
          const first = data.errors[0];
          this._setOptimistic("rejected");
          this._announce("Validation error: " + (first.message || "invalid"));
          this._emit("hedron-data-validation-error", first);
          const cell = this.querySelector(
            'tr[data-row-key="' +
              cssEscape(first.row_key || "") +
              '"] td[data-field="' +
              cssEscape(first.field || "") +
              '"]'
          );
          // Do not steal focus; announce only (OPTIMISTIC-039).
          if (cell) cell.setAttribute("data-invalid", "1");
        } else {
          this._setOptimistic("rejected");
          this._announce("Save failed");
        }
      } catch (err) {
        if (err && err.name === "AbortError") return;
        this._setOptimistic("rejected");
        this._announce("Save failed");
      } finally {
        this._saving = false;
        const again = this._saveAgain;
        this._saveAgain = false;
        if (
          again &&
          (this._pending.length || this._inserts.length || this._deletes.length)
        ) {
          queueMicrotask(() => this._save());
        }
      }
    }
  }

  if (typeof customElements !== "undefined" && !customElements.get(TAG)) {
    customElements.define(TAG, HedronDataEditor);
  }

  const HOST_SELECTOR = "[data-hedron-module='hedron-data:tabulator-editor']";

  function matchingElements(root, selector) {
    const elements = [];
    if (root && root.matches && root.matches(selector)) elements.push(root);
    if (root && root.querySelectorAll) {
      elements.push(...root.querySelectorAll(selector));
    }
    return elements;
  }

  function enhance(root) {
    // ABI path: markup already is <hedron-data-editor>; ensure connected boot.
    matchingElements(root, TAG + "[data-hedron-element], " + TAG).forEach((el) => {
      if (el._boot && !el._booted) el._boot();
    });
    // Legacy div host upgrade path (0.38 fixtures).
    matchingElements(root, HOST_SELECTOR).forEach((host) => {
      if (host.tagName && host.tagName.toLowerCase() === TAG) return;
      if (host.querySelector(TAG)) return;
      const el = document.createElement(TAG);
      host.appendChild(el);
      const fallback = host.querySelector(":scope > .hedron-data-editor-fallback");
      if (fallback) {
        fallback.setAttribute("data-hedron-fallback", "upgraded");
        fallback.setAttribute("aria-hidden", "true");
      }
    });
  }

  function disposeAll(root) {
    matchingElements(root, TAG).forEach((el) => el.dispose && el.dispose());
  }

  const api = {
    enhance,
    disposeAll,
    sanitizeFormulaCell,
    csvEscapeField,
    buildCsv,
    snapshotSaveBatch,
    rowVersionsAfterBatch,
    reconcileAfterSuccess,
    serializeSaveBody,
    readCsrfToken,
    TAG,
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
