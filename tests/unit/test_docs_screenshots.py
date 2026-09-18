from scripts.generate_docs_screenshots import OUTPUT, ROOT, SCREENSHOTS


def test_screenshot_generator_covers_all_documentation_screenshots() -> None:
    filenames = [screenshot.filename for screenshot in SCREENSHOTS]
    assert len(filenames) == len(set(filenames))
    assert set(filenames) == {path.name for path in OUTPUT.glob("*.jpg")}
    for screenshot in SCREENSHOTS:
        assert (ROOT / screenshot.app_dir / f"{screenshot.module}.py").is_file()
        assert screenshot.width > 0
        assert screenshot.height > 0
        assert (OUTPUT / screenshot.filename).read_bytes().startswith(b"\xff\xd8\xff")


def test_readme_screenshot_links_follow_the_current_main_assets() -> None:
    for package in ("hedron", "edron"):
        readme = (ROOT / "packages" / package / "README.md").read_text(encoding="utf-8")
        assert (
            f"https://raw.githubusercontent.com/eddiethedean/hedron/main/docs/assets/"
            f"{package}-showcase.jpg"
        ) in readme
        assert f"/v1.0/docs/assets/{package}-showcase.jpg" not in readme
