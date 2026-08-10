from scripts.check_external_links import extract_urls


def test_extract_urls_strips_markdown_punctuation() -> None:
    text = "See [docs](https://www.python.org/path)—then continue."
    assert extract_urls(text) == {"https://www.python.org/path"}


def test_extract_urls_ignores_placeholder_and_local_hosts() -> None:
    text = (
        "https://idp.example/callback http://127.0.0.1:8000 "
        "https://example.gradio.live https://www.python.org/x"
    )
    assert extract_urls(text) == {"https://www.python.org/x"}
