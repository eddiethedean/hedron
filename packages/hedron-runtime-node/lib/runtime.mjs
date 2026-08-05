/** HTML escaping matching Python html.escape semantics used by Hedron. */

export function escapeText(value) {
  return String(value)
    .replace(/\u0000/g, "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function escapeAttr(value) {
  return String(value)
    .replace(/\u0000/g, "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}

const VOID = new Set([
  "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
  "source", "track", "wbr",
]);

export function normalizeHtml(html) {
  return String(html).trim().replace(/>\s+</g, "><");
}

export function renderNode(node) {
  const kind = node.kind;
  if (kind === "empty") return "";
  if (kind === "text") return escapeText(node.text ?? "");
  if (kind === "trusted") return String(node.html ?? "");
  if (kind === "comment") {
    return `<!--${String(node.text ?? "").replace(/--/g, " - - ")}-->`;
  }
  if (kind === "fragment") {
    return (node.children ?? []).map(renderNode).join("");
  }
  if (kind === "element") {
    const tag = String(node.tag ?? "div").toLowerCase();
    const attrs = node.attributes ?? {};
    const parts = [];
    for (const name of Object.keys(attrs).sort()) {
      const value = attrs[name];
      if (value === null || value === false || value === undefined) continue;
      if (value === true) parts.push(String(name).toLowerCase());
      else parts.push(`${String(name).toLowerCase()}="${escapeAttr(String(value))}"`);
    }
    const attrStr = parts.length ? ` ${parts.join(" ")}` : "";
    const isVoid = Boolean(node.void) || VOID.has(tag);
    if (isVoid) return `<${tag}${attrStr}>`;
    const inner = (node.children ?? []).map(renderNode).join("");
    return `<${tag}${attrStr}>${inner}</${tag}>`;
  }
  throw new Error(`unknown node kind: ${kind}`);
}

function a11yOk(tree) {
  const seen = new Set();
  function walk(node) {
    if (node.kind !== "element") {
      return (node.children ?? []).every(walk);
    }
    const tag = String(node.tag ?? "").toLowerCase();
    const attrs = node.attributes ?? {};
    if (typeof attrs.id === "string") {
      if (seen.has(attrs.id)) return false;
      seen.add(attrs.id);
    }
    if (tag === "img" && !("alt" in attrs)) return false;
    if (tag === "button") {
      const text = (node.children ?? [])
        .filter((c) => c.kind === "text")
        .map((c) => c.text ?? "")
        .join("")
        .trim();
      const aria = attrs["aria-label"] || attrs["aria-labelledby"];
      if (!text && !aria) return false;
    }
    return (node.children ?? []).every(walk);
  }
  return walk(tree);
}

export function evaluateFixture(fixture) {
  const inp = fixture.input;
  const cap = fixture.capability;
  if (cap === "escaping" || cap === "adversarial") {
    if (inp.kind === "escape_text") return { escaped_text: escapeText(inp.text ?? "") };
    if (inp.kind === "escape_attr") return { escaped_attr: escapeAttr(inp.attr ?? "") };
    if (inp.kind === "render_tree") {
      return { html: normalizeHtml(renderNode(inp.tree)) };
    }
    if (inp.expect_error) return { error_code: fixture.expected.error_code };
  }
  if (cap === "identity") {
    return { identity: `id:${String(inp.logical_id ?? "").trim()}` };
  }
  if (cap === "diagnostics") {
    return { diagnostic_code: fixture.expected.diagnostic_code };
  }
  if (cap === "artifact-version") {
    return { artifact_version: String((inp.artifact ?? {}).version ?? "") };
  }
  if (cap === "rendering") {
    return { html: normalizeHtml(renderNode(inp.tree)) };
  }
  if (cap === "accessibility") {
    return { a11y_ok: a11yOk(inp.tree) };
  }
  throw new Error(`unsupported ${cap}/${inp.kind}`);
}

function compare(expected, actual) {
  for (const key of Object.keys(expected)) {
    if (expected[key] === null || expected[key] === undefined) continue;
    let exp = expected[key];
    let act = actual[key];
    if (key === "html") {
      exp = normalizeHtml(exp);
      act = normalizeHtml(act ?? "");
    }
    if (exp !== act) {
      return `${key} mismatch: expected=${JSON.stringify(exp)} actual=${JSON.stringify(act)}`;
    }
  }
  return null;
}

export function runFixtures(fixtures) {
  const results = [];
  for (const fixture of fixtures) {
    try {
      const actual = evaluateFixture(fixture);
      const detail = compare(fixture.expected, actual);
      results.push({
        fixture_id: fixture.id,
        contract_version: fixture.contract_version ?? "hedron-portable-1",
        capability: fixture.capability,
        passed: detail === null,
        detail: detail
          ? `fixture=${fixture.id} contract=${fixture.contract_version ?? "hedron-portable-1"} capability=${fixture.capability}: ${detail}`
          : "",
      });
    } catch (err) {
      results.push({
        fixture_id: fixture.id,
        contract_version: fixture.contract_version ?? "hedron-portable-1",
        capability: fixture.capability,
        passed: false,
        detail: `fixture=${fixture.id} contract=${fixture.contract_version ?? "hedron-portable-1"} capability=${fixture.capability}: evaluator error: ${err}`,
      });
    }
  }
  return results;
}
