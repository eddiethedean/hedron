from hedron_jinja.providers import (
    charts_provider_manifest,
    data_provider_manifest,
    provider_available,
)


def test_provider_manifests_and_availability() -> None:
    data = data_provider_manifest()
    charts = charts_provider_manifest()
    assert data.feature_id == "hedron.data"
    assert charts.feature_id == "hedron.charts"
    assert provider_available("hedron.data")
    assert provider_available("hedron.charts")
