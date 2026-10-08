# Meraxes Guide

Meraxes is a semi-analytic galaxy formation model that couples the evolution
of high-redshift galaxies to reionization, IGM heating and the 21-cm signal.

| Page | Contents |
|---|---|
| [Introduction](docs/index.md) | What Meraxes models and predicts |
| [Quick start](docs/getting-started.md) | Dependencies, compilation and running |
| [Inputs](docs/inputs.md) | Simulation data, tables and parameters |
| [Workflow](docs/workflow.md) | Execution flow and physical connections |
| [Outputs](docs/outputs.md) | Files, datasets, attributes and units |
| [Post-processing tools](docs/post-processing.md) | DRAGONS readers, histories, grids and statistics |
| [Formulas](docs/formulas/index.md) | Physical prescriptions and numerical definitions |
| [References](docs/references.md) | Model and development papers |

## Build the documentation

```sh
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`. Read the Docs uses `.readthedocs.yaml`.
