# Posit Connect reference

This FastAPI content bundle imports `HedronWorkbench` and exercises the same
page, fragment, CSRF, asset, OpenAPI, redirect, diagnostics, WebSocket, and
outside-Workbench behavior as the licensed Workbench reference.

`scripts/realconnect_029.sh` creates a temporary deployment bundle and vendors
the local `hedron`, `hedron-core`, and `hedron-workbench` source trees so the
Connect smoke validates this checkout rather than a published package.

The deployed app also builds an email-invite-style URL with
`app.external_url_for(...)`. The smoke proves that Connect's public content
mount appears exactly once, the token query value is encoded, the base header
is corroborated by Connect's protected runtime marker and ASGI `root_path`, and
server licensing/bootstrap secrets were not inherited by the content process.

The script reads the product-license-shaped `CONNECT_API_KEY` from the repo-root
`.env`, maps it to the image's `PCT_LICENSE` only for startup, creates an
ephemeral bootstrap publishing key, and gracefully stops Connect so the license
can deactivate.

The image is pinned by digest, `.env` is parsed as data rather than sourced as
shell code, temporary files use mode `0700`/`0600`, and the publishing key and
deployment bundle are deleted during cleanup. The bootstrap secret file is
deleted as soon as the temporary publishing key has been created.
