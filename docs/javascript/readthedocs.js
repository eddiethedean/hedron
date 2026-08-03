document.addEventListener("DOMContentLoaded", function () {
  // Trigger Read the Docs' search addon instead of Material MkDocs default.
  const input = document.querySelector(".md-search__input");
  if (input !== null) {
    input.addEventListener("focus", () => {
      document.dispatchEvent(new CustomEvent("readthedocs-search-show"));
    });
  }
});

// Integrate the Read the Docs version menu into the Material header.
document.addEventListener("readthedocs-addons-data-ready", function (event) {
  const config = event.detail.data();
  const versions = config?.versions;
  if (!versions?.current) return;

  const versioning = document.createElement("div");
  versioning.className = "md-version";

  const button = document.createElement("button");
  button.className = "md-version__current";
  button.type = "button";
  button.setAttribute("aria-label", "Select documentation version");
  button.textContent = versions.current.slug || "latest";
  versioning.append(button);

  const list = document.createElement("ul");
  list.className = "md-version__list";
  for (const version of versions.active || []) {
    let url;
    try {
      url = new URL(version.url, window.location.origin);
    } catch {
      continue;
    }
    if (url.protocol !== "https:" && url.protocol !== "http:") continue;

    const item = document.createElement("li");
    item.className = "md-version__item";
    const link = document.createElement("a");
    link.className = "md-version__link";
    link.href = url.href;
    link.textContent = version.slug;
    item.append(link);
    list.append(item);
  }
  versioning.append(list);

  const currentVersions = document.querySelector(".md-version");
  if (currentVersions !== null) {
    currentVersions.remove();
  }
  const topic = document.querySelector(".md-header__topic");
  if (topic !== null) {
    topic.append(versioning);
  }
});
