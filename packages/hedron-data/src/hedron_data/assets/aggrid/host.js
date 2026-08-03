/**
 * AG Grid Community host shim for Hedron DataEditor.
 * Expects window.agGrid from a locally served Community build.
 * Payload arrives as non-executable JSON via data-hedron-payload.
 */
(function () {
  function mount(el) {
    if (!window.agGrid || !window.agGrid.createGrid) return;
    const raw = el.getAttribute("data-hedron-payload");
    if (!raw) return;
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      return;
    }
    const columns = (payload.columns || []).map(function (col) {
      return {
        field: col.name,
        headerName: col.label || col.name,
        editable: !col.read_only && !col.hidden,
        hide: !!col.hidden,
      };
    });
    window.agGrid.createGrid(el, {
      columnDefs: columns,
      rowData: payload.rows || [],
      suppressClickEdit: false,
    });
  }

  function scan(root) {
    (root || document)
      .querySelectorAll("hedron-data-aggrid, [data-hedron-grid='aggrid']")
      .forEach(mount);
  }

  document.addEventListener("DOMContentLoaded", function () {
    scan(document);
  });
  document.body &&
    document.body.addEventListener("htmx:afterSwap", function (ev) {
      scan(ev.target);
    });
})();
