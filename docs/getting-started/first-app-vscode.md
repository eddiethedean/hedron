# Your first application with VS Code

This guide is for you if you can read and write Python but have not built an application
before. It assumes no experience with VS Code, virtual environments, web servers, or the
terminal. By the end, you will have a small Hedron web application, make a visible change,
add a second page, run a check, and run an automated test.

Allow 30–60 minutes the first time. Most of that time is learning the tools; the application
itself is small.

If you already use an editor and terminal comfortably, the shorter
[five-minute quickstart](quickstart.md) covers the same initial application.

## What the tools do

You will use four tools. They have separate jobs:

| Tool | What it does |
|---|---|
| Python | Runs your application code |
| VS Code | Lets you browse and edit the project's files |
| Terminal | Lets you give text commands to your computer |
| Web browser | Sends requests to your running application and displays its pages |

The **project folder** is the directory containing all the files for one application. A
**server** is a program that waits for browser requests and sends responses. During development,
the server runs on your computer and is reachable only through a local address such as
`http://127.0.0.1:8000`.

!!! note "How to read command blocks"

    Type one line at a time and press **Enter**. Do not type a leading `$`, `>`, or the text
    shown by your terminal prompt. Commands are different from Python statements: enter them in
    the terminal, not in `app.py` and not at a Python `>>>` prompt.

## Before you start

Install:

1. CPython **3.11–3.14** from [python.org](https://www.python.org/downloads/) or your
   operating system's package manager.
2. [Visual Studio Code](https://code.visualstudio.com/Download).
3. [`uv`](https://docs.astral.sh/uv/getting-started/installation/), which creates an isolated
   Python environment and installs the packages the project declares.

The Python extension published by Microsoft is helpful but not required to run the app. In
VS Code, select the Extensions icon on the left, search for **Python**, check that the publisher
is Microsoft, and choose **Install**.

Use [Installation](installation.md) if you need Windows-specific Python commands, a `pip`
alternative, a corporate package index, or offline installation.

## 1. Open a folder and a terminal

1. Open VS Code.
2. Choose **File → Open Folder**.
3. Create or select a folder where you keep programming projects, such as `python-projects`.
   Do not select the Hedron repository itself.
4. If VS Code asks whether you trust the folder, trust it only if it is a folder you created or
   obtained from a source you trust.
5. Choose **Terminal → New Terminal**.

The terminal appears at the bottom of VS Code. The final part of its prompt should name the folder
you opened. Confirm the tools are available:

=== "macOS / Linux"

    ```bash
    python3 --version
    uv --version
    pwd
    ```

=== "Windows PowerShell"

    ```powershell
    py -3 --version
    uv --version
    Get-Location
    ```

The Python result must be between 3.11 and 3.14. `pwd` and `Get-Location` mean “print working
directory”; the result tells you which folder subsequent commands affect.

If a command says it cannot find Python or `uv`, reopen VS Code after installing the tool. If it
still fails, stop here and use [Installation troubleshooting](installation.md#common-install-problems).

## 2. Create the project

Run this command in the terminal:

```bash
uvx --from "hedron>=0.40.0,<0.41" hedron new my-hedron-app
```

This asks `uv` to run the bounded current-train Hedron project creator in a temporary environment.
It creates a new folder named `my-hedron-app`; it does not install Hedron globally or change
unrelated Python projects.

Now open the newly created project:

1. Choose **File → Open Folder** again.
2. Select `python-projects/my-hedron-app`.
3. Choose **Terminal → New Terminal** if VS Code did not open a new terminal automatically.

You should see these entries in VS Code's Explorer panel:

```text
my-hedron-app/
├── app.py
├── components/
└── pyproject.toml
```

- `app.py` is your application code.
- `pyproject.toml` names the project, supported Python version, and dependencies.
- `components/` is where project-owned reusable interface components can go later.

If your terminal is still in the parent `python-projects` folder, enter `cd my-hedron-app`.
Running commands from the wrong folder is one of the most common beginner problems.

## 3. Create the project environment

Run:

```bash
uv sync
```

`uv sync` reads `pyproject.toml`, creates a private `.venv` directory, and installs the declared
packages there. The leading dot makes `.venv` a hidden folder on many systems. Do not edit files
inside it and do not copy it between computers.

Confirm that the project environment can import Hedron:

```bash
uv run python -c "import hedron; print(hedron.__version__)"
```

Expect the current `0.40.x` train (`0.40.0` or a later patch). The words `uv run` mean “run the
following command using this project's environment.” They prevent the common mistake of using a
different Python from the one where the packages were installed.

If you installed the VS Code Python extension, choose **View → Command Palette**, run
**Python: Select Interpreter**, and select the interpreter whose path contains
`my-hedron-app/.venv`. This gives editor completion and diagnostics the same environment used by
the terminal commands.

## 4. Run the application

Start the development server:

```bash
uv run uvicorn app:app --reload
```

Here is what each part means:

| Part | Meaning |
|---|---|
| `uv run` | Use this project's Python environment |
| `uvicorn` | Start the web server |
| `app:app` | Import the object named `app` from the file `app.py` |
| `--reload` | Restart the server after you save a Python file |

Leave this terminal running. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
You should see **Hello from hedron new** and a **Refresh status** button.

Click **Refresh status**. The timestamp changes without the whole page reloading. The browser asked
for a small page fragment, and Hedron replaced only the declared status region.

`127.0.0.1` means your own computer. Other people cannot use this development URL, and starting a
development server is not the same as publishing an application.

### Stop and restart the server

Click inside the terminal and press **Ctrl+C**. On macOS this is still the Control key, not Command.
Wait until the ordinary prompt returns. Run the same `uv run uvicorn ...` command to start it again.

Do not close a busy terminal to stop the server unless Ctrl+C fails. A clean stop makes errors and
unfinished work easier to understand.

## 5. Make a visible edit

In VS Code's Explorer, select `app.py`. Find:

```python
Text("Hello from hedron new")
```

Change it to:

```python
Text("Hello from Ada")
```

Use your own name if you prefer, then save with **File → Save** or **Ctrl+S** (`Cmd+S` on macOS).
Uvicorn reports a reload in the terminal. Refresh the browser if it does not refresh automatically.

If the terminal displays a Python traceback after the edit, read the final few lines first. They
usually name the file, line number, and immediate error. Undo the edit with **Ctrl+Z** (`Cmd+Z` on
macOS), save, and confirm the server starts again.

## 6. Understand the generated application

You do not need to memorize `app.py`. Its main pieces are:

1. **Imports** make Hedron and Python names available.
2. `app = Hedron(...)` creates the application object Uvicorn imports.
3. `status = app.region(...)` gives the replaceable status area a stable identity.
4. `@app.page("/")` connects the browser path `/` to the `home` Python function.
5. `@app.fragment("/status", ...)` connects the refresh request to a smaller response.

When a browser opens `/`, Hedron calls `home()` and renders its returned `Page`. When the button
requests `/status`, Hedron calls `refresh_status()` and checks that the request targets the declared
region. This explicit page/fragment boundary is the core interaction model.

Read [What is HTMX?](what-is-htmx.md) for a visual explanation after the application works.

## 7. Add a second page

At the end of `app.py`, add:

```python


@app.page("/about")
def about() -> Page:
    return Page(Text("This is my second page."), title="About")
```

Save the file, then open [http://127.0.0.1:8000/about](http://127.0.0.1:8000/about). The decorator
connects the `/about` URL to the function immediately below it.

If you get a 404 response, check that you saved `app.py`, the line begins with `@app.page`, and the
server reloaded without an error.

## 8. Ask Hedron to check the app

Open a second terminal with **Terminal → New Terminal** so the first can keep running. Run:

```bash
uv run hedron --app app:app check
```

The check imports your application and examines its routes and configuration. Informational
findings on a development scaffold are normal. An error includes a `HED-*` code and remediation.
Use the code in [Error codes](../guides/error-codes.md) or search the documentation for it.

## 9. Add one automated test

A test repeats an observation for you and fails loudly when the result changes. Stop the server or
use the second terminal, then install test-only dependencies:

```bash
uv add --dev pytest httpx
```

In VS Code:

1. Select **New Folder** in the Explorer and name it `tests`.
2. Select **New File** inside that folder and name it `test_app.py`.
3. Paste and save:

```python
from fastapi.testclient import TestClient

from app import app


def test_home_page() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Hello from Ada" in response.text
```

Run the test:

```bash
uv run pytest
```

Expect a green result ending in `1 passed`. This test does not open a real browser or require the
development server; it sends an HTTP request directly to the application in memory.

Try changing `Ada` in the test to a different name and rerun it. Read the failure, restore the
correct name, and confirm it passes again. Learning what a useful failure looks like makes future
errors less intimidating.

## 10. Your normal development loop

After the first setup, a work session is usually:

1. Open the `my-hedron-app` folder in VS Code.
2. Run `uv sync` if `pyproject.toml` or the lockfile changed.
3. Run `uv run uvicorn app:app --reload`.
4. Edit and save files; observe the browser and terminal.
5. Run `uv run pytest` and `uv run hedron --app app:app check`.
6. Stop the server with Ctrl+C before closing the terminal.

The `.venv` contains installed packages; your source of truth is `pyproject.toml` plus your own
Python files. If `.venv` is damaged, it is normally safe to remove that one project-local directory
and run `uv sync` again. Never delete a directory unless you have confirmed its exact path.

## Optional: make a Git checkpoint

Git records versions of your source files. It is separate from GitHub and does not publish anything
by itself. Before the first commit, create a `.gitignore` file in VS Code containing:

```gitignore
.venv/
__pycache__/
*.pyc
.env
```

Then run:

```bash
git init
git status
git add app.py pyproject.toml uv.lock tests .gitignore
git commit -m "Create first Hedron app"
```

If Git asks for your name or email, follow the exact configuration commands it prints. Do not use
`git add .` until you understand which files `git status` says will be recorded. Never commit
passwords, API keys, session secrets, `.env`, or `.venv`. Git does not record the empty
`components/` directory; it will appear in a later commit after you add a component file.

## Common problems

| What you see | What it usually means | What to do |
|---|---|---|
| `uv: command not found` | VS Code was open before `uv` was installed, or `uv` is not on PATH | Reopen VS Code; then use [Installation](installation.md) |
| `No pyproject.toml found` | The terminal is in the parent or another folder | Open `my-hedron-app`; confirm with `pwd` / `Get-Location` |
| `ModuleNotFoundError: hedron` | The command used a different Python environment | Run `uv sync`, then prefix the command with `uv run` |
| `Address already in use` | Another server already uses port 8000 | Stop it, or add `--port 8001` and open that port |
| Browser says it cannot connect | The server is stopped or failed during import | Read the terminal; fix the final traceback and restart |
| Browser shows 404 | The URL does not match a registered route | Check `/`, `/about`, spelling, and the terminal request log |
| Changes do not appear | File was not saved, or reload failed | Save; inspect the server terminal for a traceback |
| The prompt is `>>>` | You started the interactive Python interpreter | Enter `exit()` and run the command at the ordinary terminal prompt |

See the larger [Troubleshooting guide](../guides/troubleshooting.md) when the suggested fix does not
resolve the problem.

## Continue from here

Use the same project for the next lessons:

1. [What is HTMX?](what-is-htmx.md)
2. [Add another updating region](../guides/htmx-interactions.md)
3. [Post a minimal form](../guides/minimal-form.md)
4. [Follow the complete learning path](learning-path.md)

If your development environment is Posit Workbench, use the parallel
[first application in Posit Workbench](first-app-posit-workbench.md) guide instead.
