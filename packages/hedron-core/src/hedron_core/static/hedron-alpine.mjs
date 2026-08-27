/* Hedron's pinned, CSP-safe local Alpine projection for phase 0.67.
 *
 * This deliberately uses a small data interpreter rather than Function/eval.  It
 * owns disposable local presentation only; HTMX remains the request and HTML
 * replacement authority.  The public Alpine-shaped surface is intentionally
 * narrow and idempotent so a page has one local runtime and one start operation.
 */
const VERSION = "hedron-alpine-0.67.0";
const roots = new WeakMap();
const initialized = new WeakSet();
const cleanups = new WeakMap();
const factories = new Map();
const bundles = new Map();
const conditionalClones = new WeakMap();
const repeatedClones = new WeakMap();
let started = false;

function own(value, key) {
  return Object.prototype.hasOwnProperty.call(value, key);
}

function rootFor(element) {
  let cursor = element;
  while (cursor) {
    if (roots.has(cursor)) return cursor;
    cursor = cursor.parentElement;
  }
  return null;
}

function scopeFor(element) {
  const root = rootFor(element);
  return root ? roots.get(root) : Object.create(null);
}

function splitTopLevel(source, separator) {
  let depth = 0;
  let quote = "";
  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      if (character === quote && source[index - 1] !== "\\") quote = "";
      continue;
    }
    if (character === "'" || character === '"') {
      quote = character;
      continue;
    }
    if ("([{".includes(character)) depth += 1;
    if (")] }".replace(" ", "").includes(character)) depth -= 1;
    if (depth === 0 && source.slice(index, index + separator.length) === separator) {
      return [source.slice(0, index), source.slice(index + separator.length)];
    }
  }
  return null;
}

function readPath(path, scope, element, event) {
  const name = path.trim();
  if (name === "$el") return element;
  if (name === "$event") return event;
  if (name === "$root") return rootFor(element) || element;
  if (name === "$dispatch") {
    return (eventName, detail = {}) =>
      element.dispatchEvent(new CustomEvent(String(eventName), { bubbles: true, detail }));
  }
  const pieces = name.split(".");
  let value = scope;
  for (const piece of pieces) {
    if (value == null) return undefined;
    value = value[piece];
  }
  return value;
}

function writePath(path, value, scope) {
  const pieces = path.trim().split(".");
  if (!pieces.length || !/^[A-Za-z_$][A-Za-z0-9_$]*$/.test(pieces[0])) return;
  let target = scope;
  for (let index = 0; index < pieces.length - 1; index += 1) {
    const piece = pieces[index];
    if (!target[piece] || typeof target[piece] !== "object") target[piece] = {};
    target = target[piece];
  }
  target[pieces[pieces.length - 1]] = value;
}

function parseLiteral(source) {
  const text = source.trim();
  if (text === "true") return true;
  if (text === "false") return false;
  if (text === "null") return null;
  if (/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$/.test(text)) return Number(text);
  if ((text.startsWith('"') && text.endsWith('"')) || (text.startsWith("'") && text.endsWith("'"))) {
    return text.slice(1, -1).replace(/\\([\\'"nrt])/g, (_, character) =>
      ({ n: "\n", r: "\r", t: "\t" }[character] || character));
  }
  return undefined;
}

function callExpression(source, scope, element, event) {
  const match = source.match(/^([A-Za-z_$][A-Za-z0-9_$.]*)\((.*)\)$/s);
  if (!match) return undefined;
  const callable = readPath(match[1], scope, element, event);
  if (typeof callable !== "function") return undefined;
  const args = [];
  let rest = match[2].trim();
  while (rest) {
    const comma = splitTopLevel(rest, ",");
    const part = comma ? comma[0] : rest;
    args.push(evaluate(part, scope, element, event));
    rest = comma ? comma[1].trim() : "";
  }
  return callable.apply(scope, args);
}

function evaluate(source, scope, element, event) {
  const text = String(source || "").trim();
  if (!text) return undefined;
  const assignment = splitTopLevel(text, "=");
  if (assignment && !["==", ">=", "<=", "!=", "!=="].some((operator) => text.includes(operator))) {
    const target = assignment[0].trim();
    if (/^[A-Za-z_$][A-Za-z0-9_$.]*$/.test(target)) {
      const value = evaluate(assignment[1], scope, element, event);
      writePath(target, value, scope);
      return value;
    }
  }
  for (const operator of ["||", "&&", "!==", "===", ">=", "<=", "!=", "==", ">", "<", "+", "-"]) {
    const pair = splitTopLevel(text, operator);
    if (pair) {
      const left = evaluate(pair[0], scope, element, event);
      if (operator === "&&" && !left) return left;
      if (operator === "||" && left) return left;
      const right = evaluate(pair[1], scope, element, event);
      if (operator === "||") return left || right;
      if (operator === "&&") return left && right;
      if (operator === "===") return left === right;
      if (operator === "!==") return left !== right;
      if (operator === "==") return left == right; // eslint-disable-line eqeqeq
      if (operator === "!=") return left != right; // eslint-disable-line eqeqeq
      if (operator === ">") return left > right;
      if (operator === ">=") return left >= right;
      if (operator === "<") return left < right;
      if (operator === "<=") return left <= right;
      if (operator === "+") return left + right;
      if (operator === "-") return left - right;
    }
  }
  const literal = parseLiteral(text);
  if (literal !== undefined) return literal;
  const called = callExpression(text, scope, element, event);
  return called === undefined ? readPath(text, scope, element, event) : called;
}

function remember(element, cleanup) {
  const list = cleanups.get(element) || [];
  list.push(cleanup);
  cleanups.set(element, list);
}

function applyBinding(element, name, value) {
  if (name === "class") {
    element.className = value == null ? "" : String(value);
  } else if (name === "textContent") {
    element.textContent = value == null ? "" : String(value);
  } else if (name in element && !name.startsWith("aria-") && !name.startsWith("data-")) {
    element[name] = value;
  } else if (value === false || value == null) {
    element.removeAttribute(name);
  } else {
    element.setAttribute(name, value === true ? "" : String(value));
  }
}

function processCreated(element) {
  // Alpine-created HTMX islands must enter the existing lifecycle exactly once.
  // Hedron never injects a script or registers a plugin from a fragment.
  if (window.htmx && typeof window.htmx.process === "function" && element) {
    window.htmx.process(element);
  }
}

function refresh(root) {
  const scope = roots.get(root);
  if (!scope) return;
  const nodes = [root, ...root.querySelectorAll("[x-text], [x-show], [x-bind\\:], [x-model]")];
  for (const template of root.querySelectorAll("template[x-if]")) {
    const visible = Boolean(evaluate(template.getAttribute("x-if"), scope, template, null));
    const clones = conditionalClones.get(template) || [];
    if (visible && clones.length === 0) {
      const fragment = template.content.cloneNode(true);
      const created = [...fragment.childNodes];
      template.parentNode.insertBefore(fragment, template);
      conditionalClones.set(template, created);
      for (const element of created) {
        if (element.nodeType === 1) {
          initTree(element);
          processCreated(element);
        }
      }
    } else if (!visible && clones.length) {
      for (const element of clones) {
        if (element.nodeType === 1) destroyTree(element);
        element.remove();
      }
      conditionalClones.delete(template);
    }
  }
  for (const template of root.querySelectorAll("template[x-for]")) {
    const match = (template.getAttribute("x-for") || "").match(
      /^([A-Za-z_$][A-Za-z0-9_$]*)\s+in\s+([A-Za-z_$][A-Za-z0-9_$.]*)$/
    );
    if (!match) continue;
    const values = evaluate(match[2], scope, template, null);
    const items = Array.isArray(values) ? values : [];
    const prior = repeatedClones.get(template) || [];
    if (prior.length !== items.length) {
      for (const element of prior) {
        if (element.nodeType === 1) destroyTree(element);
        element.remove();
      }
      const created = [];
      items.forEach((item) => {
        const fragment = template.content.cloneNode(true);
        const elements = [...fragment.childNodes].filter((node) => node.nodeType === 1);
        // A repeated item must have one stable root.  Dropping arbitrary sibling
        // nodes would make cleanup and focus ownership ambiguous.
        if (elements.length !== 1) return;
        const first = elements[0];
        const key = item && typeof item === "object" ? item.id ?? item.key : item;
        if (key === undefined || key === null) return;
        first.setAttribute("x-data", JSON.stringify({ [match[1]]: item }));
        first.setAttribute("data-hedron-for-key", String(key));
        template.parentNode.insertBefore(fragment, template);
        created.push(first);
        initTree(first);
        processCreated(first);
      });
      repeatedClones.set(template, created);
    }
  }
  for (const element of nodes) {
    if (!element || !element.matches) continue;
    const text = element.getAttribute("x-text");
    if (text !== null) element.textContent = String(evaluate(text, scope, element, null) ?? "");
    const show = element.getAttribute("x-show");
    // The fallback is deliberately presentation-safe when the CSP core was
    // refused or failed integrity.  Only an explicitly optional projection may
    // be hidden; essential semantic content remains usable while the enhanced
    // runtime is unavailable.  The official Alpine runtime owns ordinary x-show
    // behavior when its integrity-checked core is present.
    if (show !== null && element.hasAttribute("data-hedron-optional")) {
      element.hidden = !Boolean(evaluate(show, scope, element, null));
    }
    for (const attribute of [...element.attributes]) {
      if (attribute.name.startsWith("x-bind:")) {
        applyBinding(element, attribute.name.slice(7), evaluate(attribute.value, scope, element, null));
      }
    }
    const bundleName = element.getAttribute("x-bind");
    if (bundleName && bundles.has(bundleName)) {
      for (const [name, value] of Object.entries(bundles.get(bundleName))) {
        applyBinding(element, name, typeof value === "function" ? value(scope) : value);
      }
    }
    const effect = element.getAttribute("x-effect");
    if (effect !== null) evaluate(effect, scope, element, null);
    const model = element.getAttribute("x-model");
    if (model !== null && document.activeElement !== element) {
      const value = readPath(model, scope, element, null);
      if (element.type === "checkbox") element.checked = Boolean(value);
      else element.value = value == null ? "" : String(value);
    }
  }
}

function initElement(element, root) {
  if (initialized.has(element)) return;
  initialized.add(element);
  const scope = roots.get(root);
  if (!scope) return;
  const disposers = [];
  const interactionKind = element.getAttribute("data-hedron-interaction");
  const interactionEvent = element.getAttribute("data-hedron-event") || "click";
  const localAction = element.getAttribute("data-hedron-local-action");
  const hasCanonicalEventHandler = [...element.attributes].some(
    (attribute) => attribute.name.startsWith(`x-on:${interactionEvent}`)
  );
  if (localAction && (interactionKind === "local" || interactionKind === "combined") && !hasCanonicalEventHandler) {
    const handler = (event) => {
      const callable = readPath(localAction, scope, element, event);
      if (typeof callable === "function") callable.call(scope, event);
      else {
        const keys = (element.getAttribute("data-hedron-state-keys") || "")
          .split(",").map((key) => key.trim()).filter(Boolean);
        const key = keys[0] || localAction;
        const current = readPath(key, scope, element, event);
        if (typeof current === "boolean") writePath(key, !current, scope);
      }
      refresh(root);
    };
    element.addEventListener(interactionEvent, handler);
    disposers.push(() => element.removeEventListener(interactionEvent, handler));
  }
  for (const attribute of [...element.attributes]) {
    if (attribute.name.startsWith("x-on:")) {
      const pieces = attribute.name.slice(5).split(".");
      const eventName = pieces.shift();
      const handler = (event) => {
        if (pieces.includes("prevent")) event.preventDefault();
        if (pieces.includes("stop")) event.stopPropagation();
        evaluate(attribute.value, scope, element, event);
        refresh(root);
      };
      element.addEventListener(eventName, handler);
      disposers.push(() => element.removeEventListener(eventName, handler));
    }
  }
  const model = element.getAttribute("x-model");
  if (model !== null) {
    const handler = (event) => {
      const value = element.type === "checkbox" ? element.checked : element.value;
      writePath(model, value, scope);
      refresh(root);
    };
    element.addEventListener("input", handler);
    element.addEventListener("change", handler);
    disposers.push(() => {
      element.removeEventListener("input", handler);
      element.removeEventListener("change", handler);
    });
  }
  if (element.hasAttribute("x-cloak")) element.removeAttribute("x-cloak");
  const init = element.getAttribute("x-init");
  if (init !== null) evaluate(init, scope, element, null);
  remember(element, () => disposers.splice(0).forEach((dispose) => dispose()));
}

function initRoot(root) {
  if (roots.has(root)) {
    for (const element of root.querySelectorAll("*")) {
      if (element.hasAttribute("x-data") && !roots.has(element)) initRoot(element);
      initElement(element, rootFor(element) || root);
    }
    refresh(root);
    return;
  }
  let data = {};
  try {
    data = JSON.parse(root.getAttribute("x-data") || "{}");
  } catch (_) {
    data = {};
  }
  const factoryName = root.getAttribute("x-data-name");
  if (factoryName && factories.has(factoryName)) data = { ...data, ...factories.get(factoryName)() };
  roots.set(root, data);
  root.setAttribute("data-hedron-alpine-root", "initialized");
  initElement(root, root);
  for (const element of root.querySelectorAll("*")) {
    if (element.hasAttribute("x-data")) initRoot(element);
    const owner = rootFor(element) || root;
    initElement(element, owner);
  }
  refresh(root);
}

function destroyTree(root) {
  const elements = [root, ...root.querySelectorAll("*")];
  for (const element of elements.reverse()) {
    const list = cleanups.get(element);
    if (list) list.splice(0).forEach((cleanup) => cleanup());
    initialized.delete(element);
    cleanups.delete(element);
    roots.delete(element);
    if (element.removeAttribute) element.removeAttribute("data-hedron-alpine-root");
  }
}

function initTree(container) {
  if (!container || !container.querySelectorAll) return;
  const rootsInContainer = [];
  if (container.matches && container.hasAttribute("x-data")) rootsInContainer.push(container);
  rootsInContainer.push(...container.querySelectorAll("[x-data]"));
  if (rootsInContainer.length) {
    for (const root of rootsInContainer) initRoot(root);
    return;
  }
  const owner = rootFor(container);
  if (owner) {
    for (const element of [container, ...container.querySelectorAll("*")]) {
      initElement(element, rootFor(element) || owner);
    }
    refresh(owner);
  }
}

function installLifecycleBridge(runtime) {
  if (runtime.__hedronLifecycleBridgeInstalled) return;
  runtime.__hedronLifecycleBridgeInstalled = true;
  const plan = document.querySelector('meta[name="hedron-browser-plan"]')?.content;
  if (plan) {
    document.addEventListener("htmx:beforeRequest", (event) => {
      const xhr = event.detail?.xhr;
      if (xhr?.setRequestHeader) xhr.setRequestHeader("X-Hedron-Browser-Plan", plan);
    });
  }
  document.addEventListener("htmx:afterProcessNode", (event) => {
    const elt = event.detail?.elt;
    if (elt) runtime.initTree(elt);
  });
  document.addEventListener("htmx:afterSwap", (event) => {
    const target = event.detail?.target || event.detail?.elt;
    if (target) runtime.initTree(target);
  });
  document.addEventListener("htmx:afterSettle", (event) => {
    const target = event.detail?.target || event.detail?.elt;
    if (target) runtime.initTree(target);
  });
  document.addEventListener("htmx:beforeCleanupElement", (event) => {
    const elt = event.detail?.elt;
    if (elt) runtime.destroyTree(elt);
  });
}

function start() {
  if (started) return;
  started = true;
  initTree(document);
  const plan = document.querySelector('meta[name="hedron-browser-plan"]')?.content;
  if (plan) {
    document.addEventListener("htmx:beforeRequest", (event) => {
      const xhr = event.detail?.xhr;
      if (xhr?.setRequestHeader) xhr.setRequestHeader("X-Hedron-Browser-Plan", plan);
    });
  }
  document.addEventListener("htmx:afterProcessNode", (event) => initTree(event.detail?.elt));
  document.addEventListener("htmx:afterSwap", (event) => initTree(event.detail?.target || event.detail?.elt));
  document.addEventListener("htmx:afterSettle", (event) => initTree(event.detail?.target || event.detail?.elt));
  document.addEventListener("htmx:beforeCleanupElement", (event) => destroyTree(event.detail?.elt));
}

const HedronProjection = {
  version: VERSION,
  start,
  initTree,
  destroyTree,
  data(name, factory) {
    if (!name || typeof factory !== "function") throw new TypeError("Alpine.data requires a name and factory");
    factories.set(String(name), factory);
  },
  bind(name, bundle) {
    if (!name || !bundle || typeof bundle !== "object") throw new TypeError("Alpine.bind requires a name and bundle");
    bundles.set(String(name), { ...bundle });
  },
  plugin(plugin) {
    if (typeof plugin === "function") plugin(Alpine);
  },
  nextTick(callback) {
    queueMicrotask(() => { if (typeof callback === "function") callback(); });
  },
};

const Alpine = window.Alpine || HedronProjection;
if (!window.Alpine) {
  window.Alpine = Alpine;
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
} else {
  window.HedronAlpine = { version: Alpine.version || "3.16.3", lifecycle: "htmx" };
  installLifecycleBridge(Alpine);
}

export { Alpine };
