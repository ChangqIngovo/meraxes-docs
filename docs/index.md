# Meraxes Guide

Meraxes follows galaxies through dark-matter halo merger forests and couples
their radiation to the ionization and thermal evolution of the intergalactic
medium. This guide connects the executable, physical prescriptions, numerical
algorithms, configuration and saved data.

![Meraxes from launch to saved output](_static/workflow.svg)

## Start here

| Task | Read |
|---|---|
| Compile Meraxes and launch a run | [Getting started](getting-started.md) |
| Supply trees, tables, fields and parameters | [Inputs and configuration](inputs.md) |
| Follow each stage from `main()` to output | [Execution workflow](workflow.md) |
| Understand gas, stars, feedback and mergers | [Galaxy physics](galaxy-physics.md) |
| Understand black holes and radiation | [Black holes and AGN](black-holes.md) |
| Calculate ionization, temperatures and 21-cm products | [IGM and 21-cm calculations](igm.md) |
| Configure source scatter and recalibration | [Stochasticity](stochasticity.md) |
| Enable Pop. III, enrichment, photometry or [O III] | [Optional physics](optional-physics.md) |
| Interpret units, gridding and parallel calculations | [Numerical conventions](numerics.md) |
| Locate galaxy fields, grid arrays and attributes | [Output reference](outputs.md) |
| Find an equation or scientific reference | [Equation index](equations.md), [References](references.md) |
| Diagnose build, run or analysis failures | [Troubleshooting](troubleshooting.md) |

## Source version

The guide is based on the latest `forests` revision inspected on 8 October 2026:
[`qyx268/meraxes-devs@90d8474`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95).
Dependencies, defaults, execution order and schemas come from this revision.
Physics pages give the implemented equations alongside the original and
subsequent development papers, beginning with
[Mutch et al. (2016)](https://doi.org/10.1093/mnras/stw1506).

`Snap` denotes a generic saved snapshot; actual HDF5 group names have the form
`SnapNNN`. Dimensions, rank counts, galaxy counts and selected products follow
the simulation and configuration. Diagrams use the example basename `meraxes`,
controlled by `FileNameGalaxies`.

```{toctree}
:maxdepth: 2
:caption: Guide

overview
getting-started
inputs
workflow
galaxy-physics
black-holes
igm
stochasticity
optional-physics
numerics
outputs
equations
troubleshooting
references
```
