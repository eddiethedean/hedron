/**
 * MapLibre host — expects window.maplibregl from local maplibre-gl.js.
 * Folium/PyDeck/GeoJSON payloads are CSP-safe JSON (no remote tile URLs required).
 * ``coord_order``: ``latlng`` (Folium default) or ``lnglat`` (MapLibre-native).
 */
(function () {
  function fail(el, message) {
    el.setAttribute("data-hedron-chart-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) el.textContent = message;
  }
  function destroy(el) {
    el._hedronMapGen = (el._hedronMapGen || 0) + 1;
    try {
      var map = el._hedronMapLibre;
      if (map && typeof map.remove === "function") {
        map.remove();
      }
    } catch (_) {
      /* ignore remove errors during swap */
    }
    el._hedronMapLibre = null;
    el.removeAttribute("data-hedron-chart-mounted");
  }
  function toLngLat(pair, coordOrder) {
    if (!Array.isArray(pair) || pair.length < 2) return [0, 0];
    if (coordOrder === "lnglat") {
      return [Number(pair[0]), Number(pair[1])];
    }
    // Folium / latlng default
    return [Number(pair[1]), Number(pair[0])];
  }
  function mount(el) {
    if (!window.maplibregl) {
      fail(el, "MapLibre runtime missing (serve local maplibre-gl.js)");
      return;
    }
    destroy(el);
    var gen = (el._hedronMapGen || 0) + 1;
    el._hedronMapGen = gen;
    var raw = el.getAttribute("data-hedron-payload");
    if (!raw) return;
    var payload;
    try {
      payload = JSON.parse(raw);
    } catch (_) {
      fail(el, "Invalid map payload JSON");
      return;
    }
    var spec = payload.spec || payload;
    var coordOrder = payload.coord_order || spec.coord_order || "latlng";
    el.style.minHeight = el.style.minHeight || "240px";
    var center = spec.center || [0, 0];
    var lngLat = toLngLat(center, coordOrder);
    var map = new window.maplibregl.Map({
      container: el,
      style: {
        version: 8,
        sources: {},
        layers: [
          {
            id: "background",
            type: "background",
            paint: { "background-color": "#e8eef5" },
          },
        ],
      },
      center: lngLat,
      zoom: Number(spec.zoom || 2),
      attributionControl: false,
    });
    el._hedronMapLibre = map;
    (spec.markers || []).forEach(function (m) {
      if (!m || !m.location) return;
      var loc = m.location;
      new window.maplibregl.Marker()
        .setLngLat(toLngLat(loc, coordOrder))
        .addTo(map);
    });
    if (spec.geojson) {
      map.on("load", function () {
        if (el._hedronMapGen !== gen || el._hedronMapLibre !== map) return;
        try {
          map.addSource("hedron-geo", { type: "geojson", data: spec.geojson });
          map.addLayer({
            id: "hedron-geo-fill",
            type: "fill",
            source: "hedron-geo",
            paint: { "fill-color": "#3388ff", "fill-opacity": 0.3 },
          });
        } catch (_) {
          /* ignore after destroy */
        }
      });
    }
    el.setAttribute("data-hedron-chart-mounted", "1");
  }
  function scan(root) {
    var base = root || document;
    var sel = '[data-hedron-chart="maplibre"]';
    if (base.matches && base.matches(sel)) mount(base);
    if (base.querySelectorAll) base.querySelectorAll(sel).forEach(mount);
  }
  function beforeSwap(ev) {
    var target = ev && ev.target;
    if (!target) return;
    var sel = '[data-hedron-chart="maplibre"]';
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
