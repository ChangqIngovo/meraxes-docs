# Meraxes Guide

A complete Sphinx + MyST guide to Meraxes: building and running the model,
input formats and parameters, execution flow, governing equations, stochastic
source prescriptions, numerical conventions and the HDF5 output schema.

The guide documents `forests` in
[`qyx268/meraxes-devs`](https://github.com/qyx268/meraxes-devs) at
[`90d8474cf41dcea646189fb86a65b7e18755ed95`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95),
the latest revision inspected on **8 October 2026**. Dependencies, defaults and
schemas come from source. Physics chapters connect the implementation to
Mutch et al. (2016) and subsequent development papers. External Sector
photometry has a separately identified source revision.

## Guide contents

| Page | Contents |
|---|---|
| [Overview](docs/overview.md) | Physical connections, source flow and diagram key |
| [Getting started](docs/getting-started.md) | Dependencies, build options, CLI and launch |
| [Inputs](docs/inputs.md) | Trees, fields, tables and the complete parameter atlas |
| [Workflow](docs/workflow.md) | Initialization, snapshot loop and output assembly |
| [Galaxy physics](docs/galaxy-physics.md) | Virial properties, gas, stars, feedback and mergers |
| [Black holes](docs/black-holes.md) | Accretion, feedback and AGN radiation |
| [IGM and 21-cm](docs/igm.md) | Ionization, thermal evolution, velocities, spectra and lightcones |
| [Stochasticity](docs/stochasticity.md) | Scatter, no-SFR, recalibration and reproducibility |
| [Optional physics](docs/optional-physics.md) | Pop. III, LW, enrichment, photometry, dust and [O III] |
| [Numerical conventions](docs/numerics.md) | Units, indexing, parallelism and resolution |
| [Outputs](docs/outputs.md) | Galaxy fields, grid datasets, attributes and master links |
| [Equations](docs/equations.md) | Cross-referenced equation index |
| [Troubleshooting](docs/troubleshooting.md) | Build, run, output and numerical diagnostics |
| [References](docs/references.md) | Bibliography and source provenance |

## Build the documentation

Use Python 3.12. These packages build the guide; Meraxes runtime dependencies
are listed in [Getting started](docs/getting-started.md).

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r docs/requirements.txt
.venv/bin/python -m sphinx -M html docs docs/_build -W --keep-going
```

On Windows, use `py -3.12 -m venv .venv` and replace `.venv/bin/python` with
`.venv\Scripts\python.exe`. Open `docs/_build/html/index.html` to read the guide.

## Read the Docs

Import this repository in [Read the Docs](https://app.readthedocs.org/) and use
`main` as its default branch. `.readthedocs.yaml` selects Python 3.12, installs
`docs/requirements.txt`, and runs Sphinx with warnings treated as failures.
After a successful build, use the project's **View docs** link. Pushes trigger
rebuilds once the project integration is connected.

## Maintain the guide

See [CONTRIBUTING.md](CONTRIBUTING.md). Editable SVGs are generated with
`python tools/generate_figures.py`; the equation index is generated with
`python tools/generate_equation_index.py`. Scientific source links are pinned
so readers can reproduce the documented implementation.
