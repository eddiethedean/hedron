from hedron_charts.optional_adapters import GraphVizAdapter, MermaidAdapter
from hedron_core.visualization import ChartAccessibility


def test_diagram_adapters() -> None:
    acc = ChartAccessibility(title="t", description="d")
    assert "digraph" in str(
        GraphVizAdapter().compile("digraph G { a -> b }", accessibility=acc).body
    )
    assert (
        MermaidAdapter().compile("graph TD; A-->B", accessibility=acc).metadata["adapter"]
        == "mermaid"
    )
