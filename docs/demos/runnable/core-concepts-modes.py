from hedron import Page, RenderMode, html, render

# PAGE: full HTML document for navigation / history restoration.
page = Page(html.div("All systems operational", id="service-status"), title="Status")
page_result = render(page, mode=RenderMode.PAGE)

# FRAGMENT: targeted content for an HTMX request.
fragment = html.div(
    "All systems operational · refreshed 12:00:00 UTC",
    id="service-status",
    role="status",
)
fragment_result = render(fragment, mode=RenderMode.FRAGMENT)

assert "<html" in page_result.html.lower()
assert "<html" not in fragment_result.html.lower()
