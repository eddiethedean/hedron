from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "packages/hedron-elements/src/hedron_elements/static/composition-041.mjs"


def test_browser_composition_draft_and_trace_runtime() -> None:
    script = f"""
      import {{ registerCompositionEdge, dispatchComposition, storeDraft, consumeDraft,
        emitBrowserTrace }} from {MODULE.as_uri()!r};
      registerCompositionEdge({{id:'edge.one', event:'hedron-change', action:'refresh',
        target:'results', detailKeys:['value'], maxDepth:4, maxPayloadBytes:128}});
      const result = await dispatchComposition('edge.one', {{detail:{{value:1}}}},
        {{authorize: async () => true, action: async (_a, detail) => detail.value + 1}});
      if (result.outcome !== 'success' || result.result !== 2) process.exit(2);
      const map = new Map();
      const storage = {{get length(){{return map.size}}, key(i){{return [...map.keys()][i]}},
        getItem(k){{return map.get(k) ?? null}},
        setItem(k,v){{map.set(k,v)}}, removeItem(k){{map.delete(k)}}}};
      const identity = {{app:'app', routeFamily:'edit', elementContract:'field',
        schemaVersion:'1', subject:'subject-fingerprint'}};
      if (!storeDraft(identity, {{title:'draft'}}, {{storage, now:1000, ttlMs:5000,
        operationId:'op'}})) process.exit(3);
      if (consumeDraft(identity, {{storage, now:2000}})?.fields.title !== 'draft') process.exit(4);
      if (consumeDraft(identity, {{storage, now:2000}}) !== null) process.exit(5);
      if (emitBrowserTrace({{correlationId:'c', elementId:'e', outcome:'success', payload:'x'}},
        () => {{}})) process.exit(6);
    """
    subprocess.run(["node", "--input-type=module", "-e", script], check=True)
