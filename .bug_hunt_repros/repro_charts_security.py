#!/usr/bin/env python3
import sys
sys.path[:0] = ["packages/hedron-charts/src", "packages/hedron-core/src"]

from hedron_charts.optional_adapters import ThreeJsAdapter
from hedron_charts.limits import reject_remote_urls
from hedron_core.visualization import ChartAccessibility, VisualizationLimits

print("=== ThreeJsAdapter accepts relative model_url (no remote gate) ===")
adapter = ThreeJsAdapter()
spec = {"model_url": "../../../secret/model.glb", "bytes": 100}
acc = ChartAccessibility(title="t", description="d").validated()
try:
    out = adapter.compile(spec, accessibility=acc, limits=VisualizationLimits(max_payload_bytes=1_000_000))
    print(f"Compiled OK: body={out.body[:120]}...")
    print("Relative path NOT rejected — browser may resolve at runtime")
except Exception as e:
    print(f"Rejected: {e}")

print("\n=== reject_remote_urls on relative path ===")
try:
    reject_remote_urls({"model_url": "../../../x.glb"})
    print("NOT rejected")
except Exception as e:
    print(f"Rejected: {e}")

print("\n=== host_render payload with </script> in title ===")
from hedron_charts.host_render import render_host_figure
from hedron_core.visualization import ChartOutput

acc = ChartAccessibility(title='</script><script>alert(1)</script>', description="d").validated()
output = ChartOutput(
    kind="chartjs",
    body='{"type":"bar","data":{"labels":["a"],"datasets":[{"data":[1]}]}}',
    accessibility=acc,
    media_type="application/json",
)
node = render_host_figure(output, host="chartjs")
# Render to string-ish repr
print(f"Rendered node type: {type(node).__name__}")
