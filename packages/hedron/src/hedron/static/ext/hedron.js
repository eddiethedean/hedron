/* Hedron's opt-in HTMX lifecycle projection for phase 0.64. */
(function () {
  "use strict";

  var requestAttribute = "data-hedron-request-state";
  var busyAttribute = "data-hedron-managed-busy";

  function elementFrom(event) {
    return event && event.detail && event.detail.elt;
  }

  function isHost(elt) {
    return !!(elt && elt.hasAttribute && elt.hasAttribute("data-hedron-state-host"));
  }

  function markBusy(elt) {
    if (!isHost(elt) || !elt.setAttribute) return;
    elt.setAttribute(requestAttribute, "pending");
    elt.setAttribute("data-hedron-state", "pending");
    if (!elt.hasAttribute("aria-busy")) {
      elt.setAttribute("aria-busy", "true");
      elt.setAttribute(busyAttribute, "true");
    }
  }

  function clearBusy(elt) {
    if (!isHost(elt) || !elt.removeAttribute) return;
    elt.removeAttribute(requestAttribute);
    if (elt.getAttribute(busyAttribute) === "true") {
      elt.removeAttribute("aria-busy");
      elt.removeAttribute(busyAttribute);
    }
  }

  function finish(elt, state) {
    if (!isHost(elt)) return;
    elt.setAttribute("data-hedron-state", state);
    clearBusy(elt);
  }

  htmx.defineExtension("hedron", {
    init: function () {},
    onEvent: function (name, event) {
      var elt = elementFrom(event);
      if (name === "htmx:beforeRequest") {
        markBusy(elt);
      } else if (name === "htmx:afterRequest") {
        finish(elt, event.detail && event.detail.successful ? "success" : "error");
      } else if (name === "htmx:sendError") {
        finish(elt, "error");
      } else if (name === "htmx:sendAbort") {
        finish(elt, "aborted");
      } else if (name === "htmx:afterSwap") {
        if (elt && htmx.trigger) htmx.trigger(elt, "hedron:afterSwap", { source: elt });
      } else if (name === "htmx:afterSettle") {
        if (elt && htmx.trigger) htmx.trigger(elt, "hedron:afterSettle", { source: elt });
      } else if (name === "htmx:beforeCleanupElement") {
        clearBusy(elt);
      }
      return true;
    }
  });
})();
