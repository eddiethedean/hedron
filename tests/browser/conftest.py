"""Browser suite note: module-scoped app fixtures reset plugin state themselves.

Function-scoped autouse reset in ``tests/conftest.py`` runs *after* module fixtures
are created, so each browser module fixture must call
``tests.browser._harness.reset_browser_plugin_state`` before constructing ``Hedron()``.

Explorer panels are especially sticky on the WebKit CI job: ``ENGINES`` lists webkit
last, so the selected-engine test is last and no later skip clears panels before the
next module starts uvicorn (duplicate ``hedron-charts-viz`` / ``HED-PLUGIN-0004``).
"""
