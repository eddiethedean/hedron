/* Backend-free shell around isolated, real Hedron/hedron-sim galleries. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const data = JSON.parse($("explorer-data").content.textContent);
  const controls = ["theme", "compare", "mode", "accent", "section", "width"];
  const title = (name) => name.charAt(0).toUpperCase() + name.slice(1);
  for (const accent of data.accents) $("accent").add(new Option(title(accent), accent));
  for (const section of data.sections) $("section").add(new Option(title(section), section));
  $("accent").value = "green";

  function selected(name) {
    return data.themes[name === "folio" ? `folio:${$("accent").value}` : name];
  }
  function tokens(exported) {
    return exported.resolved_modes[$("mode").value];
  }
  function cell(row, value, heading = false) {
    const node = document.createElement(heading ? "th" : "td");
    node.textContent = value;
    if (heading) node.scope = "row";
    row.append(node);
    return node;
  }
  function renderTokens() {
    const left = tokens(selected($("theme").value));
    const right = $("compare").value ? tokens(selected($("compare").value)) : {};
    const filter = $("token-filter").value.toLowerCase();
    const names = [...new Set([...Object.keys(left), ...Object.keys(right)])].sort();
    const rows = document.createDocumentFragment();
    let count = 0;
    for (const name of names) {
      if (!`${name} ${left[name]} ${right[name]}`.toLowerCase().includes(filter)) continue;
      const row = document.createElement("tr");
      cell(row, name, true);
      cell(row, left[name] ?? "—");
      cell(row, right[name] ?? "—");
      if ($("compare").value && left[name] !== right[name]) row.classList.add("different");
      rows.append(row);
      count++;
    }
    $("tokens").replaceChildren(rows);
    $("token-count").textContent = `${count} of ${names.length} tokens`;
  }
  function renderContracts() {
    const filter = $("component-filter").value.toLowerCase();
    const nodes = document.createDocumentFragment();
    for (const component of data.components.components) {
      if (!JSON.stringify(component).toLowerCase().includes(filter)) continue;
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = component.name || component.logical_id;
      const code = document.createElement("pre");
      code.textContent = JSON.stringify(component, null, 2);
      details.append(summary, code);
      nodes.append(details);
    }
    $("contracts").replaceChildren(nodes);
  }
  function applyFrame(frame, name) {
    const doc = frame.contentDocument;
    if (!doc?.getElementById("theme-css") || !frame.contentWindow.HedronSim) return;
    doc.documentElement.dataset.hedronTheme = selected(name).theme.name;
    doc.documentElement.dataset.theme = $("mode").value;
    doc.getElementById("theme-css").textContent = selected(name).css;
    frame.style.width = $("width").value;
    // Use the simulator itself to swap a declared, build-time gallery fragment.
    const section = $("section").value;
    if (frame.dataset.section !== section) {
      const link = doc.querySelector(`a[hx-get="/${section}"]`);
      if (link) {
        link.click();
        frame.dataset.section = section;
      }
    }
  }
  function update() {
    const name = $("theme").value;
    const compare = $("compare").value;
    $("accent").disabled = name !== "folio" && compare !== "folio";
    $("comparison").hidden = !compare;
    $("previews").classList.toggle("comparing", Boolean(compare));
    $("left-title").textContent = `${title(name)} · ${$("mode").value}`;
    $("right-title").textContent = compare ? `${title(compare)} · ${$("mode").value}` : "Comparison";
    applyFrame($("left"), name);
    if (compare) applyFrame($("right"), compare);
    renderTokens();
    const exported = selected(name);
    const factory = `${name}_theme`;
    $("python").textContent = `from hedron import Hedron\nfrom hedron_core.theme import ${factory}\n\napp = Hedron(theme=${factory}(${name === "folio" ? `accent="${$("accent").value}"` : ""}))\n# Set Page(data_theme="${$("mode").value}") for an explicit color preference.`;
    $("conformance").textContent = JSON.stringify(exported.conformance, null, 2);
    $("status").textContent = `${title(name)}${name === "folio" ? ` / ${$("accent").value}` : ""} · ${$("mode").value} · ${title($("section").value)}${compare ? ` · compared with ${title(compare)}` : ""} · all interactions stay in this browser`;
    const hash = new URLSearchParams(controls.map((id) => [id, $(id).value]));
    history.replaceState(null, "", `#${hash}`);
  }
  function download(filename, text, type) {
    const url = URL.createObjectURL(new Blob([text], { type }));
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  $("controls").addEventListener("submit", (event) => event.preventDefault());
  $("controls").addEventListener("change", update);
  $("token-filter").addEventListener("input", renderTokens);
  $("component-filter").addEventListener("input", renderContracts);
  for (const id of ["left", "right"]) $(id).addEventListener("load", () => {
    const frame = $(id);
    frame.contentWindow.addEventListener("click", (event) => {
      // Observe before sim's document-level navigation guard. Only trusted
      // gallery clicks synchronize the shell; programmatic swaps must not recurse.
      const link = event.target.closest?.("a[hx-get]");
      const section = link?.getAttribute("hx-get").slice(1);
      if (!event.isTrusted || !data.sections.includes(section)) return;
      frame.dataset.section = section;
      $("section").value = section;
      update();
    }, true);
    update();
  });
  $("export-css").addEventListener("click", () => download(`${$("theme").value}.css`, selected($("theme").value).css, "text/css"));
  $("export-json").addEventListener("click", () => download(`${$("theme").value}.json`, JSON.stringify(selected($("theme").value).design_tokens, null, 2), "application/json"));
  $("export-report").addEventListener("click", () => {
    const left = tokens(selected($("theme").value));
    const right = $("compare").value ? tokens(selected($("compare").value)) : {};
    const report = {
      schema: "hedron.docs-styles-comparison/1",
      selection: Object.fromEntries(controls.map((id) => [id, $(id).value])),
      left: selected($("theme").value),
      right: $("compare").value ? selected($("compare").value) : null,
      differences: $("compare").value ? [...new Set([...Object.keys(left), ...Object.keys(right)])].sort().filter((key) => left[key] !== right[key]).map((token) => ({ token, left: left[token] ?? null, right: right[token] ?? null })) : [],
    };
    download("hedron-style-comparison.json", JSON.stringify(report, null, 2), "application/json");
  });
  const hash = new URLSearchParams(location.hash.slice(1));
  for (const id of controls) {
    const value = hash.get(id);
    if ([...$(id).options].some((option) => option.value === value)) $(id).value = value;
  }
  renderContracts();
  update();
})();
