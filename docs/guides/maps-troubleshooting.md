# Maps troubleshooting

| Symptom | Check |
|---|---|
| No interactive map | Wait for `hedron-map[data-hedron-map-mounted='1']`. The table remains useful. |
| Origin error `HED-MAP-POLICY-0001` | Add the exact HTTPS origin to `MapPolicy.allowed_origins`. |
| Credentials error `HED-MAP-POLICY-0002` | Strip userinfo; do not put secrets in tile URLs. |
| Feature budget `HED-MAP-0001` | Cap GeoJSON at 500 features (same as core). |
| Missing pin `HED-MAP-RUNTIME-0002` | Reinstall `hedron-maps` with hashed MapLibre 5.6.1 assets. |
| WebGL/CSP/worker failure | `map-failed` fires; `.hedron-map-alternative` stays. |
| Chart map adapters changed | They did not. Folium/PyDeck/charts MapLibre 4.5.0 stay explicit. |

See [maps policy](maps-policy.md) and [migration](maps-migration.md).
