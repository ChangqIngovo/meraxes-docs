# Maintaining the Meraxes Guide

Update the guide with a specific source revision. Record its repository,
branch, full SHA and inspection date; check build configuration, parameter
registration/defaults, execution ordering, physics routines and output writers.

For each prescription, document variables and units, equations, activation
conditions, source routines and primary references. Where source and paper
materially differ, state the implemented behavior. A paper about another branch
does not establish that its prescription is active here.

Keep simulation-specific counts and dimensions out of the schema. Use `Snap`
for the conceptual hierarchy and `SnapNNN` for stored groups. Distinguish build
capabilities, runtime flags, datasets and HDF5 attributes. Derive dependencies
from build files rather than a local module list or Python environment.

## Editing and checking

1. Edit Markdown in `docs/`; add new pages to `docs/index.md`.
2. Give display equations unique MyST `:label:` values. Use `{eq}` references
   when the same equation is needed elsewhere.
3. Edit `tools/generate_figures.py` and regenerate SVGs when flows change.
4. Run `python tools/generate_equation_index.py`.
5. Build with `python -m sphinx -M html docs docs/_build -W --keep-going`.
6. Inspect affected figures, tables, equations and links in generated HTML.

Use `docs/requirements.txt` for documentation builds. Check source-file links
and bibliographic metadata when updating references. Exclude generated HTML and
local environments from version control.
