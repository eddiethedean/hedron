/**
 * MapLibre host — expects window.maplibregl from local maplibre-gl.js.
 * Folium/PyDeck/GeoJSON payloads are CSP-safe JSON (no remote tile URLs required).
 */
(function () {
  function fail(el, message) {
    el.setAttribute("data-hedron-chart-error", message);
    el.setAttribute("role", "alert");
    if (!el.textContent) el.textContent = message;
  }
  function mount(el) {
    if (!window.maplibregl) {
      fail(el, "MapLibre runtime missing (serve local maplibre-gl.js)");
      return;
    }
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
    el.style.minHeight = el.style.minHeight || "240px";
    var center = spec.center || [0, 0];
    // MapLibre expects [lng, lat]; Folium uses [lat, lng].
    var lngLat =
      Array.isArray(center) && center.length >= 2
        ? [Number(center[1]), Number(center[0])]
        : [0, 0];
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
    (spec.markers || []).forEach(function (m) {
      if (!m || !m.location) return;
      var loc = m.location;
      new window.maplibregl.Marker()
        .setLngLat([Number(loc[1]), Number(loc[0])])
        .addTo(map);
    });
    if (spec.geojson) {
      map.on("load", function () {
        map.addSource("hedron-geo", { type: "geojson", data: spec.geojson });
        map.addLayer({
          id: "hedron-geo-fill",
          type: "fill",
          source: "hedron-geo",
          paint: { "fill-color": "#3388ff", "fill-opacity": 0.3 },
        });
      });
    }
  }
  function scan(root) {
    (root || document)
      .querySelectorAll('[data-hedron-chart="maplibre"]')
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
