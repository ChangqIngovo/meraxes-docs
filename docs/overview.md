# Model overview

Meraxes is a semi-analytic galaxy-formation model built for finely spaced
simulation snapshots. It evolves baryonic reservoirs along halo merger forests,
retains stellar-population histories for delayed feedback, and places the
galaxies' radiation sources on a spatial grid. The resulting IGM fields can
suppress gas supply at later snapshots. This coupling connects galaxy
populations to reionization, thermal evolution and the 21-cm signal.

The foundational formulation is
[Mutch et al. (2016)](https://doi.org/10.1093/mnras/stw1506).
[Later development papers](references.md) introduce or study additional source,
feedback, photometric, thermal and Population III prescriptions. Equations in
this guide describe the inspected `forests` source; differences from a paper
are identified where they affect a scientific interpretation.

## Physical connections

![Gas, stars, black holes and IGM feedback](_static/galaxy-physics.svg)

Halo growth determines the gravitational potential and baryonic gas supply.
Gas cools from a hot reservoir into a cold disk, forms stars, returns metals
and energy, and moves between reservoirs through feedback and reincorporation.
Mergers combine histories and can trigger starbursts and black-hole fuel supply.
Escaped stellar and AGN radiation then enters the grid calculation.

| Component | Processes | Description |
|---|---|---|
| Halo assembly | Hosts, descendants, virial properties, types and ghosts | [Galaxy physics](galaxy-physics.md) |
| Gas cycling | Infall, cooling, reincorporation, stars, feedback and enrichment | [Galaxy physics](galaxy-physics.md) |
| Black holes | Seeds, accretion, feedback, ionizing radiation and X-rays | [Black holes](black-holes.md) |
| Radiation sources | Escaped cumulative stellar mass, escaped SFR and effective AGN quantities | [Stochasticity](stochasticity.md), [IGM](igm.md) |
| Ionization and UVB | Excursion-set ionization, recombinations and persistent feedback | [IGM](igm.md) |
| Thermal history | X-ray heating, ionization, Lyα coupling and spin temperature | [IGM](igm.md) |
| 21-cm products | Brightness, velocities, spectra and lightcones | [IGM](igm.md) |
| Extensions | Minihalos, Pop. III, LW, external enrichment, SEDs and [O III] | [Optional physics](optional-physics.md) |

## From sources to fields

![Galaxy sources and simulation fields entering the IGM](_static/source-flow.svg)

The grid named `stars` is a saved spatial dataset containing cell sums of
escaped cumulative stellar source mass. It is produced by
`construct_baryon_grids()`. Standard, Population III and stochastic prescriptions
determine the deposited quantities. The [output reference](outputs.md) defines
its units, companion grids and activation conditions within the `Snap/Grids`
inventory.

Density comes from the simulation. Thermal calculations use SFR and AGN X-ray
histories; ionization uses enabled stellar and AGN source budgets. Brightness
depends on neutral fraction, density, spin temperature when enabled, and the
active velocity treatment. Source grids, galaxy records and derived observables
therefore describe related stages of the same calculation.

## Execution and model selection

The [workflow](workflow.md) separates initialization, the snapshot loop and
final output assembly. In the coupled path, a snapshot's galaxies evolve before
its new IGM fields are calculated. Photoheating feedback samples the available
persistent history; the feedback arrow connects successive snapshots.

| Configuration level | Examples | Reference |
|---|---|---|
| Compile-time capabilities | `USE_STOCHASTICITY`, `USE_MINI_HALOS`, `CALC_MAGS`, `USE_CUDA` | [Build options](getting-started.md) |
| Runtime prescriptions | Star formation, SN, escape fractions, UVB, recombinations and thermal physics | [Parameter atlas](inputs.md) |
| Saved products | Output snapshots, brightness, spectra, lightcones and diagnostics | [Inputs](inputs.md), [Outputs](outputs.md) |

The default parameter file supplies values, not a universal calibration. A
consistent run combines simulation cosmology and units, compatible trees and
fields, sufficient history storage, enabled capabilities and a scientific
parameter set.

## Saved data

Writing ranks produce galaxy catalogue files; distributed grid products are
written collectively to snapshot grid files. Rank 0 assembles the master with
metadata, snapshot groups and relative external links. `Core<rank>` groups
follow the writing rank count. [Outputs](outputs.md) explains the hierarchy,
compound fields, attributes, blocks and slices; [Numerical conventions](numerics.md)
explains conversions and indexing.

## Diagram key

| Appearance | Meaning |
|---|---|
| Blue box | Inputs, simulation data or initialization |
| Gold box | Galaxy and black-hole evolution |
| Green box | Radiation grids and IGM calculations |
| Purple box or arrow | Feedback to galaxy evolution |
| Red box | Saved files, datasets or summaries |
| Dashed box | Separately enabled product or calculation |
| Dashed arrow | Feedback, optional connection or bypass, as labeled |

Color identifies a role; it does not encode a file type or physical unit.
