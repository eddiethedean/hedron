/**
 * hedron-chart — first-party interactive chart element (phase 0.38 / RFC-0069).
 * Implements a D3-inspired SVG/Canvas renderer from a compiled ChartPlan JSON payload.
 * No remote fetches. Generation-guarded mount for HTMX lifecycle safety.
 */
const TAG = "hedron-chart";
const ABI = "1";
const instances = new Set();
let svgLabelSeq = 0;

function parsePlan(el) {
  const raw = el.getAttribute("data-hedron-payload");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (_) {
    return null;
  }
}

function emit(el, kind, detail) {
  el.dispatchEvent(
    new CustomEvent("hedron-chart-" + kind, {
      bubbles: true,
      composed: true,
      detail: Object.assign({ kind }, detail || {}),
    })
  );
}

function choosePaint(plan) {
  const decision = (plan && plan.renderer) || {};
  return decision.paint === "canvas" ? "canvas" : "svg";
}

function layoutBox(plan) {
  const layout = (plan && plan.layout) || {};
  return {
    width: Number(layout.width_hint) || 640,
    height: Number(layout.height_hint) || 360,
    margin: Number(layout.margin) || 40,
  };
}

function yValues(plan) {
  const marks = (plan && plan.marks) || [];
  const out = [];
  for (const m of marks) {
    const y = m.values && m.values.y;
    const n = Number(y);
    if (!Number.isNaN(n)) out.push(n);
  }
  return out;
}

function renderSvg(el, plan) {
  const box = layoutBox(plan);
  const marks = plan.marks || [];
  const ys = yValues(plan);
  const yMax = Math.max(1, ...ys, 1);
  const plotW = Math.max(1, box.width - 2 * box.margin);
  const plotH = Math.max(1, box.height - 2 * box.margin);
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("width", String(box.width));
  svg.setAttribute("height", String(box.height));
    svg.setAttribute("role", "img");
  const uid = `hc-${++svgLabelSeq}`;
  const titleId = `${uid}-title`;
  const descId = `${uid}-desc`;
  svg.setAttribute("aria-labelledby", `${titleId} ${descId}`);
  const title = document.createElementNS(ns, "title");
  title.id = titleId;
  title.textContent = (plan.accessibility && plan.accessibility.title) || "Chart";
  const desc = document.createElementNS(ns, "desc");
  desc.id = descId;
  desc.textContent = (plan.accessibility && plan.accessibility.description) || "";
  svg.appendChild(title);
  svg.appendChild(desc);

  const g = document.createElementNS(ns, "g");
  g.setAttribute("data-hedron-chart-marks", "1");
  const points = [];
  marks.forEach((mark, i) => {
    const vals = mark.values || {};
    const y = Number(vals.y);
    if (Number.isNaN(y)) return;
    const x =
      marks.length > 1
        ? box.margin + (i / (marks.length - 1)) * plotW
        : box.margin + plotW / 2;
    const py = box.margin + plotH - (y / yMax) * plotH;
    points.push([x, py, mark.identity || String(i), vals]);
  });

  const type = (marks[0] && marks[0].type) || "line";
  if (type === "bar") {
    const bw = Math.max(2, plotW / Math.max(1, points.length) - 4);
    points.forEach(([x, py, id, vals]) => {
      const rect = document.createElementNS(ns, "rect");
      rect.setAttribute("x", String(x - bw / 2));
      rect.setAttribute("y", String(py));
      rect.setAttribute("width", String(bw));
      rect.setAttribute("height", String(box.margin + plotH - py));
      rect.setAttribute("fill", "var(--hedron-chart-series-1, #2563eb)");
      rect.setAttribute("tabindex", "0");
      rect.setAttribute("data-hedron-mark", id);
      rect.addEventListener("focus", () =>
        emit(el, "focus", { identity: id, values: vals })
      );
      rect.addEventListener("click", () =>
        emit(el, "select", { identity: id, values: vals })
      );
      g.appendChild(rect);
    });
  } else if (type === "point") {
    points.forEach(([x, py, id, vals]) => {
      const c = document.createElementNS(ns, "circle");
      c.setAttribute("cx", String(x));
      c.setAttribute("cy", String(py));
      c.setAttribute("r", "4");
      c.setAttribute("fill", "var(--hedron-chart-series-1, #2563eb)");
      c.setAttribute("tabindex", "0");
      c.setAttribute("data-hedron-mark", id);
      c.addEventListener("focus", () => emit(el, "focus", { identity: id, values: vals }));
      c.addEventListener("click", () => emit(el, "select", { identity: id, values: vals }));
      g.appendChild(c);
    });
  } else {
    if (type === "area" && points.length) {
      const area = document.createElementNS(ns, "polygon");
      const baseY = box.margin + plotH;
      const pts = points
        .map(([x, py]) => `${x},${py}`)
        .concat([`${points[points.length - 1][0]},${baseY}`, `${points[0][0]},${baseY}`])
        .join(" ");
      area.setAttribute("points", pts);
      area.setAttribute("fill", "var(--hedron-chart-series-1, #2563eb)");
      area.setAttribute("fill-opacity", "0.25");
      g.appendChild(area);
    }
    const poly = document.createElementNS(ns, "polyline");
    poly.setAttribute("fill", "none");
    poly.setAttribute("stroke", "var(--hedron-chart-series-1, #2563eb)");
    poly.setAttribute("stroke-width", "2");
    poly.setAttribute("points", points.map(([x, py]) => `${x},${py}`).join(" "));
    g.appendChild(poly);
    points.forEach(([x, py, id, vals]) => {
      const c = document.createElementNS(ns, "circle");
      c.setAttribute("cx", String(x));
      c.setAttribute("cy", String(py));
      c.setAttribute("r", "3");
      c.setAttribute("fill", "var(--hedron-chart-series-1, #2563eb)");
      c.setAttribute("tabindex", "0");
      c.setAttribute("data-hedron-mark", id);
      c.addEventListener("mouseenter", () =>
        emit(el, "inspect", { identity: id, values: vals })
      );
      c.addEventListener("focus", () => emit(el, "focus", { identity: id, values: vals }));
      c.addEventListener("click", () => emit(el, "select", { identity: id, values: vals }));
      g.appendChild(c);
    });
  }
  svg.appendChild(g);
  return svg;
}

function renderCanvas(el, plan) {
  const box = layoutBox(plan);
  const canvas = document.createElement("canvas");
  canvas.width = box.width;
  canvas.height = box.height;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", (plan.accessibility && plan.accessibility.title) || "Chart");
  const ctx = canvas.getContext("2d");
  if (!ctx) return canvas;
  const ys = yValues(plan);
  const yMax = Math.max(1, ...ys, 1);
  const marks = plan.marks || [];
  const plotW = Math.max(1, box.width - 2 * box.margin);
  const plotH = Math.max(1, box.height - 2 * box.margin);
  ctx.strokeStyle = "#2563eb";
  ctx.fillStyle = "#2563eb";
  ctx.beginPath();
  marks.forEach((mark, i) => {
    const y = Number(mark.values && mark.values.y);
    if (Number.isNaN(y)) return;
    const x =
      marks.length > 1
        ? box.margin + (i / (marks.length - 1)) * plotW
        : box.margin + plotW / 2;
    const py = box.margin + plotH - (y / yMax) * plotH;
    if (i === 0) ctx.moveTo(x, py);
    else ctx.lineTo(x, py);
  });
  ctx.stroke();
  // Parallel HTML navigation list for Canvas a11y.
  const nav = document.createElement("ul");
  nav.className = "hedron-chart-canvas-nav";
  nav.setAttribute("aria-label", "Chart data points");
  marks.forEach((mark) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = `${mark.identity || ""} ${JSON.stringify(mark.values || {})}`;
    btn.addEventListener("click", () =>
      emit(el, "select", { identity: mark.identity, values: mark.values || {} })
    );
    btn.addEventListener("focus", () =>
      emit(el, "focus", { identity: mark.identity, values: mark.values || {} })
    );
    li.appendChild(btn);
    nav.appendChild(li);
  });
  const wrap = document.createElement("div");
  wrap.appendChild(canvas);
  wrap.appendChild(nav);
  return wrap;
}

function dropKeydown(el) {
  if (el._hedronChartKeydown) {
    el.removeEventListener("keydown", el._hedronChartKeydown);
    el._hedronChartKeydown = null;
  }
}

function cleanup(el) {
  el._hedronChartGen = (el._hedronChartGen || 0) + 1;
  dropKeydown(el);
  if (el._hedronChartRo) {
    try {
      el._hedronChartRo.disconnect();
    } catch (_) {}
    el._hedronChartRo = null;
  }
  const host = el.querySelector("[data-hedron-chart-host]");
  if (host) host.innerHTML = "";
  el.removeAttribute("data-hedron-chart-mounted");
  instances.delete(el);
}

function mount(el) {
  cleanup(el);
  const gen = (el._hedronChartGen || 0) + 1;
  el._hedronChartGen = gen;
  const plan = parsePlan(el);
  if (!plan) {
    el.setAttribute("data-hedron-chart-error", "missing or invalid ChartPlan payload");
    return;
  }
  let host = el.querySelector("[data-hedron-chart-host]");
  if (!host) {
    host = document.createElement("div");
    host.setAttribute("data-hedron-chart-host", "1");
    el.prepend(host);
  }
  host.innerHTML = "";
  const paint = choosePaint(plan);
  const node = paint === "canvas" ? renderCanvas(el, plan) : renderSvg(el, plan);
  host.appendChild(node);
  el.setAttribute("data-hedron-chart-mounted", "1");
  el.setAttribute("data-hedron-paint", paint);
  instances.add(el);

  if (typeof ResizeObserver !== "undefined") {
    el._hedronChartRo = new ResizeObserver(() => {
      if (el._hedronChartGen !== gen) return;
      // Re-render on resize using the same plan.
      mount(el);
    });
    el._hedronChartRo.observe(el);
  }

  function onKey(ev) {
    if (el._hedronChartGen !== gen) return;
    if (ev.key === "Escape") emit(el, "reset", {});
    if (ev.key === "Enter") emit(el, "inspect", {});
  }
  dropKeydown(el);
  el._hedronChartKeydown = onKey;
  el.addEventListener("keydown", onKey);
}

class HedronChart extends HTMLElement {
  static get observedAttributes() {
    return ["data-hedron-payload"];
  }
  connectedCallback() {
    mount(this);
  }
  disconnectedCallback() {
    cleanup(this);
  }
  attributeChangedCallback() {
    if (this.isConnected) mount(this);
  }
}

if (!customElements.get(TAG)) {
  customElements.define(TAG, HedronChart);
}

function scan(root) {
  const base = root || document;
  if (base.matches && base.matches(TAG)) mount(base);
  if (base.querySelectorAll) base.querySelectorAll(TAG).forEach(mount);
}
function beforeSwap(ev) {
  const target = ev && ev.target;
  if (!target) return;
  if (target.matches && target.matches(TAG)) cleanup(target);
  if (target.querySelectorAll) target.querySelectorAll(TAG).forEach(cleanup);
}
function oobTarget(ev) {
  return (ev && ev.detail && ev.detail.elt) || (ev && ev.target) || null;
}

document.addEventListener("DOMContentLoaded", () => scan(document));
document.addEventListener("htmx:afterSwap", (ev) => scan(ev.target));
document.addEventListener("htmx:beforeSwap", beforeSwap);
document.addEventListener("htmx:oobAfterSwap", (ev) => scan(oobTarget(ev)));
document.addEventListener("htmx:oobBeforeSwap", (ev) => beforeSwap({ target: oobTarget(ev) }));
document.addEventListener("htmx:load", (ev) => scan(ev.target));

export const hedronChartInstanceCount = () => instances.size;
export { TAG, ABI, mount, cleanup, scan };
