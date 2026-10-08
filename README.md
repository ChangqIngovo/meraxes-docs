# Meraxes documentation

A Sphinx + MyST starter for Meraxes documentation, with local HTML builds and
Read the Docs hosting. The pages are starter outlines; expand and verify them
against the Meraxes version being documented.

| Page | Purpose |
|---|---|
| `docs/overview.md` | Introduce execution flow, galaxy evolution, IGM calculations and saved outputs. |
| `docs/stochasticity.md` | Document source prescriptions, controls, equations and reproducible run examples. |
| `docs/index.md` | Provide the homepage and navigation. |

## Build locally

Use Python 3.12. Run all commands from the repository root.

Linux / macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r docs/requirements.txt
.venv/bin/python -m sphinx -M html docs docs/_build -W --keep-going
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r docs/requirements.txt
.\.venv\Scripts\python.exe -m sphinx -M html docs docs/_build -W --keep-going
```

Open `docs/_build/html/index.html` to preview the site. Rebuild after editing the
Markdown pages. Add new pages to the `toctree` in `docs/index.md`.

## Publish with Read the Docs

1. Sign in at [Read the Docs](https://app.readthedocs.org/) using GitHub.
2. Import this GitHub repository as a project.
3. Set **Default branch** to `main` and complete the import.
4. Check **Builds**, then select **View docs** after a successful build.

The root `.readthedocs.yaml` selects Python 3.12, installs
`docs/requirements.txt`, and builds using `docs/conf.py`. Push documentation
changes to `main` to trigger subsequent builds.
