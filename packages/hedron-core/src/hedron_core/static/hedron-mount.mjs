const meta = document.querySelector('meta[name="hedron-mount-path"]');
const mountPath = (meta?.content || "").replace(/\/$/, "");

function localPath(path) {
  if (
    typeof path !== "string" ||
    !path.startsWith("/") ||
    path.startsWith("//") ||
    path.includes("\\") ||
    /[\u0000-\u001f\u007f]/.test(path)
  ) {
    throw new TypeError("Hedron local paths must start with one slash");
  }
  const suffixAt = Math.min(
    ...[path.indexOf("?"), path.indexOf("#")].filter((index) => index >= 0),
    path.length,
  );
  const pathname = path.slice(0, suffixAt);
  let decoded = pathname;
  if (decoded.split("/").some((segment) => segment === "." || segment === "..")) {
    throw new TypeError("Hedron local paths must not contain traversal");
  }
  for (let round = 0; round < 3; round += 1) {
    let next;
    try {
      next = decodeURIComponent(decoded);
    } catch {
      throw new TypeError("Hedron local paths must use valid percent encoding");
    }
    if (next === decoded) break;
    decoded = next;
    if (
      decoded.startsWith("//") ||
      decoded.includes("\\") ||
      decoded.split("/").some((segment) => segment === "." || segment === "..")
    ) {
      throw new TypeError("Hedron local paths must not contain traversal");
    }
  }
  if (!mountPath || pathname === mountPath || pathname.startsWith(`${mountPath}/`)) return path;
  return pathname === "/"
    ? `${mountPath}/${path.slice(1)}`
    : `${mountPath}${path}`;
}

function websocketUrl(path) {
  const url = new URL(localPath(path), window.location.href);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}

const runtime = Object.freeze({
  mountPath,
  href: localPath,
  fetch: (path, options) => window.fetch(localPath(path), options),
  eventSource: (path, options) => new EventSource(localPath(path), options),
  websocketUrl,
  websocket: (path, protocols) => new WebSocket(websocketUrl(path), protocols),
});

Object.defineProperty(window, "Hedron", {
  value: runtime,
  configurable: false,
  enumerable: true,
  writable: false,
});
