# Introduction

**Meraxes is a semi-analytic galaxy formation model for studying the first
stars, galaxies and black holes, and their effects on the intergalactic medium
(IGM).** It follows galaxy growth through dark-matter halo merger trees and
couples their ultraviolet and X-ray emission to the ionization and thermal
state of the surrounding gas.

During cosmic dawn and the Epoch of Reionization, radiation from early
sources heated the IGM and ionized its neutral hydrogen. Galaxy surveys
measure the luminous sources, while the redshifted 21-cm signal probes the
neutral gas around them. Connecting these observations requires a model
that links the abundance and properties of galaxies to the radiation they
produce and the response of the IGM.

## Galaxies and reionization

Meraxes was developed within the DRAGONS project to follow this connection
in both space and time ({ref}`Mutch et al. 2016 <ref-mutch2016>`).
The underlying N-body simulation supplies halo masses, positions and merger
histories. Semi-analytic prescriptions then evolve the gas, stars, metals
and black holes associated with each halo. This approach combines galaxy
formation histories with the large volumes needed to describe the growth
and overlap of ionized regions.

A merger tree connects a halo to its progenitors and descendants; a forest
groups connected trees. Meraxes advances the galaxy population one snapshot
at a time. At each snapshot, emission from galaxies across the volume
contributes to shared radiation fields. Their local ionization histories and
radiation backgrounds then influence gas accretion in subsequent snapshots.
This coupling allows galaxies to affect neighbours well beyond their own
merger trees.

| Component | Physical role |
|---|---|
| Gas and stars | Gas accretion and cooling supply star formation; stellar evolution returns mass, metals and energy. |
| Black holes | Accretion and mergers grow black holes; active galactic nuclei provide radiation and feedback. |
| Radiation and the IGM | A modified **21cmFAST** calculation follows ionized regions, X-ray heating, spin temperature and the 21-cm signal. |
| Photoheating feedback | The evolving ultraviolet background reduces the gas supply of susceptible low-mass haloes. |
| Early stellar populations | Optional mini-halo physics follows metal-free stars, molecular cooling, Lyman–Werner radiation and enrichment. |

The principal extensions describe AGN growth and radiation
({ref}`Qin et al. 2017 <ref-qin2017x>`), stellar spectra and dust
({ref}`Qiu et al. 2019 <ref-qiu2019>`), IGM heating and the 21-cm signal
({ref}`Balu et al. 2023 <ref-balu2023>`), and Population III stars
({ref}`Ventura et al. 2024 <ref-ventura2024>`).

## From galaxies to observables

The galaxy population provides stellar masses, star-formation rates, gas
and metal reservoirs, black-hole properties and luminosities. Stellar
population modelling connects star-formation histories to ultraviolet
luminosities, colours and luminosity functions, allowing comparison with
high-redshift galaxy surveys.

```{figure} _static/meraxes-glfs.jpg
:alt: Galaxy ultraviolet luminosity functions at redshifts 5 to 20, with model curves and observational measurements.
:width: 100%

Galaxy UV luminosity functions: model predictions (black curves) and observational measurements (grey symbols). [Meraxes](https://github.com/qyx268/meraxes-devs/blob/forests/output/results/figs/glfs.jpg); [figure licence](_static/MERAXES-LICENSE.txt).
```

The IGM calculation predicts the neutral fraction and gas temperatures
throughout the volume. These fields determine whether neutral hydrogen
appears in 21-cm absorption or emission against the cosmic microwave
background. Coeval maps describe individual times; lightcones show the
evolution along the line of sight, while power spectra quantify the
spatial fluctuations. Together, galaxy and 21-cm observables connect the
sources of radiation to the timing and structure of cosmic heating and
reionization.

```{figure} _static/meraxes-lightcones.jpg
:alt: Four 21-cm brightness-temperature lightcones showing absorption, emission and reionization between redshifts about 30 and 5.
:width: 100%

21-cm lightcones for four model configurations. Warm colours show absorption and blue shows emission; the panels illustrate changes in the heating and reionization histories. [Meraxes](https://github.com/qyx268/meraxes-devs/blob/forests/output/results/figs/lcs.jpg); [figure licence](_static/MERAXES-LICENSE.txt).
```

## Using this guide

Start with [Configuration and compilation](getting-started.md), then follow
[Inputs](inputs.md), [Workflow](workflow.md) and [Outputs](outputs.md).
[Formulas](formulas/index.md) collects the physical and numerical
prescriptions in one place.

The complementary [DRAGONS package](https://meraxes-devs.github.io/dragons/)
reads and analyses Meraxes outputs, and
[Sector](https://github.com/meraxes-devs/sector) supplies spectral synthesis
and photometry.

```{toctree}
:maxdepth: 2
:caption: Guide

getting-started
inputs
workflow
outputs
formulas/index
references
```
