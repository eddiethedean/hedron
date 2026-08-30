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
const repeatedSignatures = new WeakMap();
let started = false;

function reportRuntimeIssue(root, code, detail) {
  if (!(root instanceof Element)) return;
  root.setAttribute("data-hedron-alpine-status", "degraded");
  root.dispatchEvent(new CustomEvent("hedron:alpine-error", {
    bubbles: true,
    detail: { code, detail: String(detail || "") },
  }));
}

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
  if (text.startsWith("!")) return !evaluate(text.slice(1), scope, element, event);
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

function ownedNodes(root, selector) {
  return [root, ...root.querySelectorAll(selector)].filter(
    (element) => element === root || rootFor(element) === root,
  );
}

function coerceModelValue(value, modifiers) {
  if (modifiers.includes("trim") && typeof value === "string") value = value.trim();
  if (modifiers.includes("number")) {
    const number = value === "" ? null : Number(value);
    if (number === null || Number.isNaN(number)) return value;
    value = number;
  }
  if (modifiers.includes("boolean")) {
    if (value === "true" || value === true) return true;
    if (value === "false" || value === false) return false;
  }
  return value;
}

function modelValue(element, modifiers, current) {
  if (element.type === "checkbox") {
    if (Array.isArray(current)) {
      const value = coerceModelValue(element.value, modifiers);
      const next = current.filter((item) => item !== value);
      if (element.checked) next.push(value);
      return next;
    }
    return element.checked;
  }
  if (element.type === "radio") return element.checked ? coerceModelValue(element.value, modifiers) : current;
  if (element.tagName === "SELECT" && element.multiple) {
    return [...element.selectedOptions].map((option) => coerceModelValue(option.value, modifiers));
  }
  return coerceModelValue(element.value, modifiers);
}

function modelBinding(element) {
  const attribute = [...element.attributes].find(
    (candidate) => candidate.name === "x-model" || candidate.name.startsWith("x-model."),
  );
  if (!attribute) return null;
  return { path: attribute.value, modifiers: attribute.name.split(".").slice(1) };
}

function modelEventName(element, modifiers) {
  if (modifiers.includes("blur")) return "blur";
  if (modifiers.includes("enter")) return "keydown";
  if (modifiers.includes("lazy") || modifiers.includes("change")) return "change";
  if (element.type === "checkbox" || element.type === "radio" || element.tagName === "SELECT") return "change";
  return "input";
}

function modelDuration(modifiers, kind) {
  const index = modifiers.indexOf(kind);
  if (index < 0) return 0;
  const value = modifiers[index + 1] || "250ms";
  const match = value.match(/^(\d+)(ms|s)$/);
  if (!match) return 250;
  return Number(match[1]) * (match[2] === "s" ? 1000 : 1);
}

function refresh(root) {
  const scope = roots.get(root);
  if (!scope) return;
  const nodes = ownedNodes(root, "*").filter((element) =>
    element.hasAttribute("x-text")
      || element.hasAttribute("x-show")
      || [...element.attributes].some((attribute) =>
        attribute.name.startsWith("x-bind:") || attribute.name.startsWith("x-model"),
      ),
  );
  for (const template of ownedNodes(root, "template[x-if]")) {
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
  for (const template of ownedNodes(root, "template[x-for]")) {
    const match = (template.getAttribute("x-for") || "").match(
      /^([A-Za-z_$][A-Za-z0-9_$]*)\s+in\s+([A-Za-z_$][A-Za-z0-9_$.]*)$/
    );
    if (!match) continue;
    const values = evaluate(match[2], scope, template, null);
    const items = Array.isArray(values) ? values : [];
    const prior = repeatedClones.get(template) || [];
    let signature = "";
    try { signature = JSON.stringify(items); } catch (_) { signature = String(items.length); }
    if (prior.length !== items.length || repeatedSignatures.get(template) !== signature) {
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
      repeatedSignatures.set(template, signature);
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
    const binding = modelBinding(element);
    if (binding !== null && document.activeElement !== element) {
      const value = readPath(binding.path, scope, element, null);
      if (element.type === "checkbox") {
        element.checked = Array.isArray(value)
          ? value.some((item) => String(item) === String(element.value))
          : Boolean(value);
      } else if (element.type === "radio") element.checked = String(value) === String(element.value);
      else if (element.tagName === "SELECT" && element.multiple) {
        const selected = Array.isArray(value) ? value.map(String) : [];
        [...element.options].forEach((option) => { option.selected = selected.includes(option.value); });
      }
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
      const listenerTarget = pieces.includes("window") ? window
        : pieces.includes("document") || pieces.includes("outside") ? document : element;
      const keyNames = {
        enter: "Enter", escape: "Escape", tab: "Tab", space: " ",
        up: "ArrowUp", down: "ArrowDown", left: "ArrowLeft", right: "ArrowRight",
        home: "Home", end: "End", delete: "Delete", backspace: "Backspace",
      };
      const keyModifiers = pieces.filter((piece) => own(keyNames, piece));
      const duration = pieces.includes("debounce") ? modelDuration(pieces, "debounce")
        : pieces.includes("throttle") ? modelDuration(pieces, "throttle") : 0;
      let timer = null;
      let lastRun = 0;
      const handler = (event) => {
        if (pieces.includes("self") && event.target !== element) return;
        if (pieces.includes("outside") && element.contains(event.target)) return;
        if (keyModifiers.length && !keyModifiers.includes(
          Object.keys(keyNames).find((key) => keyNames[key] === event.key),
        )) return;
        if (keyModifiers.length && !event.type.startsWith("key")) return;
        if (pieces.includes("ctrl") && !event.ctrlKey) return;
        if (pieces.includes("shift") && !event.shiftKey) return;
        if (pieces.includes("alt") && !event.altKey) return;
        if (pieces.includes("meta") && !event.metaKey) return;
        if (pieces.includes("prevent")) event.preventDefault();
        if (pieces.includes("stop")) event.stopPropagation();
        const run = () => {
          evaluate(attribute.value, scope, element, event);
          refresh(root);
        };
        if (pieces.includes("debounce")) {
          if (timer !== null) clearTimeout(timer);
          timer = setTimeout(run, duration);
        } else if (pieces.includes("throttle")) {
          if (Date.now() - lastRun >= duration) {
            lastRun = Date.now();
            run();
          }
        } else run();
      };
      listenerTarget.addEventListener(eventName, handler, {
        once: pieces.includes("once"),
        capture: pieces.includes("capture"),
        passive: pieces.includes("passive"),
      });
      disposers.push(() => {
        if (timer !== null) clearTimeout(timer);
        listenerTarget.removeEventListener(eventName, handler, {
          capture: pieces.includes("capture"),
        });
      });
    }
  }
  const binding = modelBinding(element);
  if (binding !== null) {
    const model = binding.path;
    const modifiers = binding.modifiers;
    const eventName = modelEventName(element, modifiers);
    const handler = (event) => {
      if (element.type === "radio" && !element.checked) return;
      if (eventName === "keydown" && event.key !== "Enter") return;
      const current = readPath(model, scope, element, event);
      writePath(model, modelValue(element, modifiers, current), scope);
      refresh(root);
    };
    element.addEventListener(eventName, handler);
    disposers.push(() => {
      element.removeEventListener(eventName, handler);
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
  } catch (error) {
    reportRuntimeIssue(root, "invalid-x-data", error);
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
