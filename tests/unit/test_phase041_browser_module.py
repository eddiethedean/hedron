from __future__ import annotations

import json
import subprocess
from pathlib import Path

from hedron_elements.composition import CompositionEdge

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


def test_python_payload_registers_in_js_runner() -> None:
    """#256: Python as_payload keys match registerCompositionEdge."""
    edge = CompositionEdge(
        id="e1",
        event="ev",
        action="act",
        target="t1",
        detail_keys=("x",),
        max_depth=4,
        max_payload_bytes=128,
        concurrency="queue",
    )
    payload = json.dumps(edge.as_payload())
    script = f"""
      import {{ registerCompositionEdge, dispatchComposition,
        clearCompositionEdges }} from {MODULE.as_uri()!r};
      const edge = {payload};
      registerCompositionEdge(edge);
      const ok = await dispatchComposition('e1', {{detail:{{x:1}}}},
        {{action: async () => 7}});
      if (ok.outcome !== 'success' || ok.result !== 7) process.exit(2);
      const denied = await dispatchComposition('e1', {{detail:{{y:1}}}},
        {{action: async () => 7}});
      if (denied.code !== 'HED-COMPOSE-0002') process.exit(3);
      clearCompositionEdges();
    """
    subprocess.run(["node", "--input-type=module", "-e", script], check=True)


def test_queue_concurrency_serializes_overlapping_dispatches() -> None:
    """#256: concurrency=queue must not start the second action until the first finishes."""
    script = f"""
      import {{ registerCompositionEdge, dispatchComposition,
        clearCompositionEdges }} from {MODULE.as_uri()!r};
      registerCompositionEdge({{id:'q1', event:'ev', action:'act', target:'t1',
        detailKeys:['n'], concurrency:'queue'}});
      const started = [];
      const resolvers = [];
      const action = async (_a, detail) => new Promise((resolve) => {{
        started.push(detail.n);
        resolvers.push(resolve);
      }});
      const first = dispatchComposition('q1', {{detail:{{n:1}}}}, {{action}});
      const second = dispatchComposition('q1', {{detail:{{n:2}}}}, {{action}});
      await new Promise((r) => setTimeout(r, 20));
      if (started.join() !== '1') process.exit(2);
      resolvers[0]('a');
      await new Promise((r) => setTimeout(r, 20));
      if (started.join() !== '1,2') process.exit(3);
      resolvers[1]('b');
      const results = await Promise.all([first, second]);
      if (results[0].result !== 'a' || results[1].result !== 'b') process.exit(4);
      clearCompositionEdges();
    """
    subprocess.run(["node", "--input-type=module", "-e", script], check=True)
