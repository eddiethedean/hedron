/**
 * AG Grid Community host for Hedron DataEditor.
 * Expects window.agGrid from a locally served Community build.
 * Payload arrives as non-executable JSON via data-hedron-payload.
 * Supports clientSide and infinite row models; emits typed CustomEvents.
 */
(function () {
  function fail(el, message) {
    el.setAttribute("data-hedron-grid-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) {
      el.textContent = message;
    }
    if (typeof console !== "undefined" && console.error) {
      console.error("[hedron-data-aggrid]", message);
    }
  }

  function emit(el, name, detail) {
    el.dispatchEvent(
      new CustomEvent(name, {
        bubbles: true,
        composed: true,
        detail: detail || {},
      })
    );
  }

  function columnDefs(payload) {
    return (payload.columns || []).map(function (col) {
      return {
        field: col.name || col.field,
        headerName: col.label || col.headerName || col.name || col.field,
        editable: !col.read_only && !col.hidden && col.writable !== false,
        hide: !!col.hidden,
        sortable: col.sortable !== false,
        filter: col.filterable !== false,
      };
    });
  }

  function bindGridEvents(el, api) {
    if (!api || !api.addEventListener) return;
    api.addEventListener("selectionChanged", function () {
      var rows = [];
      try {
        rows = api.getSelectedRows() || [];
      } catch (_) {}
      emit(el, "hedron-data-selection", {
        kind: "selection",
        count: rows.length,
        rows: rows,
      });
    });
    api.addEventListener("cellValueChanged", function (ev) {
      emit(el, "hedron-data-edit", {
        kind: "edit",
        row_key: ev && ev.data ? ev.data.id || ev.node && ev.node.id : null,
        field: ev && ev.colDef ? ev.colDef.field : null,
        value: ev ? ev.newValue : null,
        old_value: ev ? ev.oldValue : null,
      });
    });
    api.addEventListener("viewportChanged", function (ev) {
      emit(el, "hedron-data-viewport", {
        kind: "viewport",
        first: ev ? ev.firstRow : null,
        last: ev ? ev.lastRow : null,
      });
    });
    api.addEventListener("paginationChanged", function () {
      emit(el, "hedron-data-pagination", {
        kind: "pagination",
        page: api.paginationGetCurrentPage ? api.paginationGetCurrentPage() : null,
      });
    });
  }

  function infiniteDatasource(el, payload) {
    var blockSize = (payload.blockSize || payload.block_size || 100) | 0;
    if (blockSize < 1) blockSize = 100;
    return {
      getRows: function (params) {
        emit(el, "hedron-data-pagination", {
          kind: "infinite-block",
          start_row: params.startRow,
          end_row: params.endRow,
          block_size: blockSize,
          sort: params.sortModel || [],
          filter: params.filterModel || {},
        });
        // Apps may reply by setting rows on the element; default uses payload.rows slice.
        var rows = payload.rows || [];
        var slice = rows.slice(params.startRow, params.endRow);
        var last =
          typeof payload.total === "number"
            ? payload.total
            : params.endRow > rows.length
              ? rows.length
              : -1;
        params.successCallback(slice, last);
      },
    };
  }

  function destroy(el) {
    var api = el._hedronAgGridApi;
    try {
      if (api && typeof api.destroy === "function") api.destroy();
    } catch (_) {
      /* ignore teardown errors while HTMX replaces the host */
    }
    delete el._hedronAgGridApi;
    el.removeAttribute("data-hedron-grid-mounted");
  }

  function mount(el) {
    destroy(el);
    if (!window.agGrid || !window.agGrid.createGrid) {
      fail(el, "AG Grid Community runtime missing (serve local ag-grid-community.min.js)");
      return;
    }
    var raw = el.getAttribute("data-hedron-payload");
    if (!raw) {
      fail(el, "Missing data-hedron-payload");
      return;
    }
    var payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      fail(el, "Invalid data-hedron-payload JSON");
      return;
    }
    var rowModel =
      el.getAttribute("data-row-model") ||
      payload.rowModel ||
      payload.row_model ||
      "clientSide";
    var options = {
      columnDefs: columnDefs(payload),
      suppressClickEdit: false,
      rowSelection: payload.rowSelection || "multiple",
    };
    if (rowModel === "infinite") {
      options.rowModelType = "infinite";
      options.cacheBlockSize = payload.blockSize || payload.block_size || 100;
      options.datasource = infiniteDatasource(el, payload);
    } else {
      options.rowData = payload.rows || [];
    }
    var api = window.agGrid.createGrid(el, options);
    el._hedronAgGridApi = api;
    el.setAttribute("data-hedron-grid-mounted", "1");
    bindGridEvents(el, api);
  }

  function scan(root) {
    var base = root || document;
    var sel = "hedron-data-aggrid, [data-hedron-grid='aggrid']";
    if (base.matches && base.matches(sel)) mount(base);
    if (base.querySelectorAll) base.querySelectorAll(sel).forEach(mount);
  }

  function beforeSwap(ev) {
    var target = ev && ev.target;
    if (!target) return;
    var sel = "hedron-data-aggrid, [data-hedron-grid='aggrid']";
    if (target.matches && target.matches(sel)) destroy(target);
    if (target.querySelectorAll) target.querySelectorAll(sel).forEach(destroy);
  }

  function oobTarget(ev) {
    return (ev && ev.detail && ev.detail.elt) || (ev && ev.target) || null;
  }

  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.addEventListener("htmx:afterSwap", function (ev) {
    scan(ev.target);
  });
  document.addEventListener("htmx:beforeSwap", beforeSwap);
  document.addEventListener("htmx:oobAfterSwap", function (ev) {
    scan(oobTarget(ev));
  });
  document.addEventListener("htmx:oobBeforeSwap", function (ev) {
    beforeSwap({ target: oobTarget(ev) });
  });
  document.addEventListener("htmx:load", function (ev) {
    scan(ev.target);
  });
})();
