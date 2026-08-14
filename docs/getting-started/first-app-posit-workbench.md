# Your first application in Posit Workbench

This guide is for Python users who are new to application development, terminals, and Posit
Workbench. You will create the same small Hedron application as the local beginner guide, but run
it correctly inside a remote Workbench session.

The primary path uses a **VS Code session in Posit Workbench**. Workbench administrators decide
which editors and package sources are available, so your screen may have additional choices. If VS
Code is not offered, see [If your organization uses RStudio Pro](#if-your-organization-uses-rstudio-pro).

Allow 30–60 minutes. You need a Workbench URL and sign-in method from your organization; you do not
need to install VS Code on your own computer.

## Workbench and your app are different things

Posit Workbench gives you a remote development session. Your editor, terminal, Python process, and
files run on an organization-managed Linux server rather than directly on your laptop.

Your Hedron application is a second web server started inside that session. Workbench gives the
app a temporary, authenticated proxy URL. Therefore:

- do not open `http://127.0.0.1:8000` on your laptop;
- do not hard-code a Workbench `/s/.../p/...` path in Python;
- do use the `hedron-posit` launcher so paths, redirects, assets, HTMX requests, and cookies agree;
- remember that running in Workbench is development, not publication to Posit Connect.

For a local computer instead, use [Your first application with VS Code](first-app-vscode.md).

## Before you start

Ask your Workbench administrator or team lead for:

- the Workbench sign-in URL;
- a session image or environment containing CPython **3.11–3.14**;
- access to your organization's Python package index or PyPI;
- permission to start a VS Code session and proxied development web server;
- the right project directory if your team uses shared or mounted storage.

Hedron supports Posit Workbench **2025.05.1 or newer** on `linux/amd64`; see the current
[compatibility contract](../COMPATIBILITY.md) before treating a different version or architecture
as Supported.

Official Workbench references:
[session management](https://docs.posit.co/ide/server-pro/user/posit-workbench/guide/session-management.html) ·
[starting VS Code](https://docs.posit.co/ide/server-pro/user/vs-code/getting-started/) ·
[proxied servers](https://docs.posit.co/ide/server-pro/user/vs-code/guide/proxying-web-servers.html).

## 1. Start one Workbench session

1. Sign in to the Posit Workbench home page.
2. In **Projects**, select **+ New Session**.
3. Choose **VS Code**.
4. Give the session a useful name such as `hedron-first-app`.
5. If resource choices appear, use your organization's recommended development profile. Hedron's
   beginner app does not require a GPU.
6. Select **Launch**.

The exact options depend on administrator configuration. If VS Code is missing, that is not an
application error; ask the administrator which editor is supported.

Use one active Workbench session per project. Multiple sessions editing and running the same files
can overwrite changes or compete for ports.

## 2. Learn the Workbench VS Code screen

The browser-based VS Code session has the same main areas as desktop VS Code:

| Area | Purpose |
|---|---|
| Explorer on the left | Browse project folders and files |
| Editor in the center | Read and change a selected file |
| Terminal at the bottom | Run commands on the Workbench server |
| Posit icon in the Activity Bar | Open proxied web servers and return to Workbench tools |

Choose **Terminal → New Terminal**. Type one command per line and press Enter; do not type the
terminal's `$` prompt.

Check the remote environment:

```bash
python3 --version
uv --version
pwd
```

Python must report 3.11–3.14. `pwd` prints the current remote directory. Paths such as
`/home/your-name` belong to the Workbench server, not your laptop.

If `uv` is unavailable, do not install system-wide software or use `sudo`. Ask whether your team
provides a module, internal installer, or approved virtual-environment workflow, then use the
[pip fallback](#pip-fallback-without-uv).

## 3. Create the remote project

Choose a private project location approved by your organization. The following uses
`~/projects`, where `~` means your remote home directory:

```bash
mkdir -p ~/projects
cd ~/projects
uvx --from "hedron>=0.40.0,<0.41" hedron new my-workbench-app
cd my-workbench-app
uv add "hedron-posit>=0.40.0,<0.41"
```

These commands create the project, make its isolated `.venv`, install the declared dependencies,
and add the Workbench-aware adapter to `pyproject.toml`. They do not alter other users' projects.

Open the project in the editor with **File → Open Folder**, then select
`~/projects/my-workbench-app`. Open a new terminal and confirm:

```bash
pwd
uv run python -c "import hedron, hedron_posit; print(hedron.__version__)"
```

Expect the path to end in `my-workbench-app` and the version to be on the current `0.40.x` train
(`0.38.0` or a later patch).

The project contains:

```text
my-workbench-app/
├── app.py
├── components/
├── pyproject.toml
└── uv.lock
```

The lockfile records the exact resolved package set. Commit it with the app; do not edit it by
hand.

## 4. Make the app Workbench-aware

Open `app.py`. Change the Hedron import and application constructor while leaving the generated
page, status region, and fragment intact.

Change:

```python
from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap
```

to:

```python
from hedron import Page, RefreshButton, Stack, Text, html, swap
from hedron_posit import HedronPosit
```

Then change:

```python
app = Hedron(
```

to:

```python
app = HedronPosit(
```

Save the file. `HedronPosit` behaves like ordinary `Hedron` outside Posit products, while exposing
the Workbench and Connect deployment contracts when their trusted runtime evidence is present.

The generated `session_secret="replace-in-production"` fallback is acceptable only for this local
development exercise. Never commit a real secret. Your deployment should supply
`HEDRON_SESSION_SECRET` through your organization's approved secret mechanism.

## 5. Check Workbench resolution

Before importing or starting the app, run:

```bash
uv run hedron-posit check
```

The result should identify Workbench evidence and a safe loopback bind. The check is deliberately
secret-free and does not start a server. A `HED-POSIT-*` or `HED-WB-*` error includes a remediation;
do not work around it by hard-coding a session path.

## 6. Run the application

Start the Workbench-aware development launcher:

```bash
uv run hedron-posit run app:app --reload
```

Leave the terminal running. The launcher binds a loopback port, asks Workbench for this session's
temporary browser mount, exports that mount before importing `app.py`, and serves the application.
This is why plain `uvicorn app:app --reload` is not the preferred Workbench command.

To open the app from a Workbench VS Code session:

1. Select the **Posit** icon in the left Activity Bar.
2. Expand **Proxied Servers**.
3. Select the server for `my-workbench-app` (the entry also shows its port).
4. Allow VS Code to open the link if it asks about an external website.

You should see **Hello from hedron new**. Select **Refresh status** and confirm the timestamp
changes without a full-page reload.

The browser URL may contain a path like `/s/.../p/...`. It is temporary and specific to the
Workbench session. Copying it into `app.py`, email, tests, or configuration will break when the
session changes.

### What should work under the prefix

The first page, refresh request, CSS, browser assets, redirects, and Hedron-owned cookie paths
should all carry the Workbench mount exactly once. Symptoms such as an unstyled page, HTMX 403, or
a URL containing the mount twice indicate a launch/configuration problem, not a reason to prepend
the path manually.

## 7. Edit and reload

In `app.py`, change:

```python
Text("Hello from hedron new")
```

to:

```python
Text("Hello from Workbench")
```

Save. The `--reload` supervisor restarts the server, and the proxied page shows the new text after
a refresh. The proxy URL should remain usable for the current session.

If the app disappears from **Proxied Servers**, first inspect the terminal. A Python syntax/import
error stops the worker from listening. Undo the last edit, save, and wait for a successful reload.

## 8. Add and run a test

Open a second terminal so the development server can remain visible. Add test dependencies:

```bash
uv add --dev pytest httpx
```

Create `tests/test_app.py` through the Explorer:

```python
from fastapi.testclient import TestClient

from app import app


def test_home_page() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Hello from Workbench" in response.text
```

Run:

```bash
uv run pytest
uv run hedron --app app:app check
```

Expect `1 passed`. This test runs directly against the application and therefore does not use the
temporary Workbench browser URL. Keep separate tests for deployment-prefix behavior when your app
begins creating redirects, downloads, callback URLs, or custom ASGI middleware.

## 9. Stop the app and leave safely

1. Click the server terminal and press **Ctrl+C**.
2. Wait for the normal prompt to return.
3. Save all edited files.
4. Return to the Workbench home page with the Posit Workbench button.
5. Exit the session when you are finished, following your organization's session-retention policy.

Closing the browser tab does not necessarily stop a Workbench session or its child processes. Stop
the development server explicitly. Workbench can also terminate idle VS Code sessions according to
administrator policy, so source files must be saved to durable project storage rather than `/tmp`.

## Your normal Workbench loop

On later days:

1. Open the project from the Workbench home page in one VS Code session.
2. Open `my-workbench-app` and confirm the terminal location with `pwd`.
3. Run `uv sync` after dependency or lockfile changes.
4. Run `uv run hedron-posit check` when the session environment or launch topology changes.
5. Run `uv run hedron-posit run app:app --reload`.
6. Open the current entry under **Posit → Proxied Servers**.
7. Edit, test, and check the app.
8. Stop the server with Ctrl+C before exiting the Workbench session.

## Pip fallback without uv

Use this only when your organization supports ordinary virtual environments and pip. From an
approved parent folder:

```bash
mkdir -p ~/projects/my-workbench-app
cd ~/projects/my-workbench-app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "hedron>=0.40.0,<0.41" "hedron-posit>=0.40.0,<0.41" "uvicorn[standard]>=0.30"
python -m hedron new my-workbench-app --path .
```

Open `pyproject.toml` and add the adapter to the `dependencies` list so another environment can
reproduce the app:

```toml
"hedron-posit>=0.40.0,<0.41",
```

Then install the declared project and run it:

```bash
python -m pip install -e .
hedron-posit run app:app --reload
```

The prompt normally begins with `(.venv)` while the environment is active. In a new terminal, run
`source .venv/bin/activate` again before project commands. Do not install into the Workbench system
Python and do not use `sudo pip`.

## If your organization uses RStudio Pro

The application and commands are the same. In an RStudio Pro session:

1. Select the **Terminal** tab next to the Console. If it is hidden, use
   **Tools → Terminal → Move Focus to Terminal**.
2. Use the **Files** pane to open `app.py` and `pyproject.toml`.
3. Run the `uv` or pip commands in Terminal, not the R Console (the R Console prompt begins with
   `>` and does not accept shell commands).
4. Start with `hedron-posit run app:app --reload` so the Workbench mount is discovered before the
   app is imported.

How a running server is opened from RStudio Pro varies with Workbench configuration. Use the URL
or viewer integration your administrator provides; do not replace the launcher with a hard-coded
mount. If your team is choosing an editor for a new Python web project, the primary VS Code path
above provides the clearest **Proxied Servers** workflow.

## Common Workbench problems

| What you see | Likely cause | What to do |
|---|---|---|
| VS Code is not a session option | It is not enabled for your account or environment | Ask the Workbench administrator which editor to use |
| `python3` is missing or too old | Session image lacks a Supported Python | Choose an approved Python environment/profile; do not replace system Python yourself |
| `uv` / pip cannot download packages | Workbench uses an internal index or blocks outbound traffic | Ask for `UV_INDEX_URL` / `PIP_INDEX_URL` or mirrored current-train Hedron wheels |
| Proxied Servers is empty | Server did not start, stopped on import, or extension is unavailable | Read the terminal; confirm a listening process; ask whether the Workbench extension is installed |
| `HED-WB-0003` | `rserver-url` is missing or unusable | Ask the administrator to repair Workbench discovery; do not guess the mount |
| Page is unstyled or links lose `/s/.../p/...` | App started without the Workbench-aware path handoff | Stop it and use `hedron-posit run app:app --reload` |
| URL contains the mount twice | Application code manually prepended the Workbench path | Return ordinary local paths and let `hedron-posit` prefix them once |
| Another user cannot open your copied URL | Workbench development URLs are session-scoped and authenticated | Publish through an approved deployment target such as Posit Connect |
| Session ended and work vanished | Files were written to temporary storage or were not saved | Use the approved durable project directory; never keep source under `/tmp` |

For deeper diagnostics, see [Posit deployments](../guides/posit.md),
[Posit Workbench](../guides/posit-workbench.md), and
[general troubleshooting](../guides/troubleshooting.md).

## Continue from here

Keep this project and continue with:

1. [What is HTMX?](what-is-htmx.md)
2. [Add another updating region](../guides/htmx-interactions.md)
3. [Post a minimal form](../guides/minimal-form.md)
4. [Understand Workbench and Connect deployment](../guides/posit.md)
5. [Follow the complete learning path](learning-path.md)

Running the app in Workbench is still a development workflow. Publishing a durable, shareable app
to Posit Connect requires an explicit deployment, environment variables/secrets, access policy,
and operational review.
