# Execution workflow

Meraxes follows galaxies through successive halo snapshots, carrying their
gas, stellar and black-hole histories forward. Galaxy evolution supplies the
radiation sources; the IGM calculation returns a spatially varying
photoheating history that regulates subsequent gas infall. The resulting
catalogues and radiation fields connect galaxy populations to reionization
and the 21-cm signal.

![Meraxes execution from launch to the master output file](_static/workflow.svg)

Blue: inputs; gold: galaxies; green: radiation; red: outputs. Purple arrows show feedback.

## From inputs to outputs

| Stage | Implementation | Operation |
|---|---|---|
| Launch | [meraxes.c][main]: `main()` | Initialize MPI. |
| Configure | [read_params.c][params]: `read_parameter_file()` | Read run, simulation and default parameters. |
| Initialize | [init.c][init]: `init_meraxes()`, `init_storage()` | Load snapshot times and physical tables; allocate galaxy and grid storage. |
| Read halos | [read_halos.c][halos], [dracarys.c][loop] | Connect galaxies to descendants, initialize new galaxies and sample stored UVB feedback. |
| Evolve galaxies | [physics/evolve.c][evolve]: `evolve_galaxies()` | Update gas, stars, metals, black holes and mergers. |
| Prepare grids | [core/reionization.c][reion-core]: `construct_baryon_grids()`; [read_grids.c][grids]: `read_grid()` | Deposit galaxy sources and read simulation density. |
| Evolve the IGM | [ComputeTs.c][thermal], [find_HII_bubbles.c][ionization] | Calculate enabled thermal fields, ionization and UVB history. |
| Calculate observables | [BrightnessTemperature.c][brightness], [ComputePowerSpectrum.c][power], [ConstructLightcone.c][lightcone] | Produce requested 21-cm brightness, power spectra and lightcones. |
| Save snapshot | [save.c][save]: `write_snapshot()`; [core/reionization.c][reion-core]: grid output | Save selected galaxy catalogues and grid products; advance the loop. |
| Finish | [save.c][save]: `create_master_file()` | Assemble links to rank files and grid files after the final snapshot. |

The loop includes intermediate snapshots between selected outputs. Complete
halo forests stay on one MPI rank; radiation grids are distributed in slabs.
`NSteps` must remain `1`. Galaxy types distinguish centrals, satellites with
resolved subhalos, and orphans awaiting merger. Temporarily missing hosts
retain their galaxies and delayed feedback histories.

## Galaxy evolution

![Gas, stars, black holes and radiation feedback](_static/galaxy-physics.svg)

Gas flows between hot, cold and ejected reservoirs; stars and black holes grow
from this supply. Metals follow these transfers and affect subsequent
cooling. The main processes within each halo group are:

Process links below open the corresponding equations; file links open the implementation.

| Process and formulas | Physical role and model choices | Implementation and controls |
|---|---|---|
| [Infall](formulas/galaxies.md#infall-and-baryon-corrections) | Supply the central galaxy according to the halo baryon budget, reduced by photoheating. | [infall.c][infall]: `gas_infall()`; [physics/reionization.c][reion-physics]: `reionization_modifier()` |
| [Cooling and return](formulas/galaxies.md#cooling-and-reincorporation) | Cool hot gas onto the central galaxy using temperature- and metallicity-dependent rates; return ejected material to the hot reservoir. | [physics/cooling.c][cooling]: `gas_cooling()`; [reincorporation.c][return]: `reincorporate_ejected_gas()`; `ReincorporationModel` |
| [Stellar returns](formulas/galaxies.md#delayed-and-instantaneous-returns) | Earlier stellar populations return gas, newly formed metals and supernova energy on their stellar-evolution timescales. Instantaneous recycling is an alternative. | [supernova_feedback.c][supernova]: `delayed_supernova_feedback()`; [stellar_feedback.c][stellar-tables]: return tables; `Flag_IRA` |
| [Star formation](formulas/galaxies.md#star-formation) | Convert cold gas into stars using a critical-density law, a pressure-dependent molecular-gas law, or a dynamical-timescale law. | [star_formation.c][star-formation]: `insitu_star_formation()`; `SfPrescription=1`, `2`, or `3` |
| [Supernova feedback](formulas/galaxies.md#reheating-and-ejection) | Reheat cold gas and eject halo gas according to the available energy and halo potential; update metal reservoirs. | [supernova_feedback.c][supernova]: `contemporaneous_supernova_feedback()`; `SnModel` |
| [Black-hole growth](formulas/galaxies.md#accretion-and-mechanical-feedback) | Accrete hot gas and consume a cold-gas reservoir supplied by mergers. Radio-mode heating reduces cooling; quasar-mode feedback reheats or ejects gas. | [blackhole_feedback.c][black-holes]: `radio_mode_BH_heating()`, `previous_merger_driven_BH_growth()` |
| [Galaxy mergers](formulas/galaxies.md#galaxy-mergers) | Merge reservoirs and stellar histories when an orphan's merger clock expires; eligible mergers trigger a starburst and feed the black-hole accretion reservoir. | [mergers.c][mergers]: `merge_with_target()`; `MergerTimeFactor`, burst parameters |

Cooling is evaluated before adding the current infall and reincorporated gas.
Delayed returns and previously queued black-hole accretion precede new star
formation; mergers follow this evolution. This order determines which gas
and feedback contributions are available during the current step.

With `USE_MINI_HALOS`, [molecular cooling](formulas/galaxies.md#molecular-cooling)
extends star formation into smaller halos, and metallicity selects
[Pop. III or Pop. II star formation](formulas/galaxies.md#population-iii-stars-and-enrichment).
Optional
Lyman–Werner radiation, streaming velocities and external enrichment modify
the onset of this activity. [PopIII.c][popiii] supplies stellar-population
properties; [metal_evo.c][metals] follows external enrichment.

## Radiation and feedback

Source deposition sums stellar and black-hole contributions in their nearest
grid cells. The [source grids](outputs.md#source-grids) then supply the
radiation calculation.

| Component and formulas | Model treatment | Implementation and controls |
|---|---|---|
| [Stellar ionizing emission](formulas/galaxies.md#ionizing-escape-fraction) | Escape fractions may depend on redshift, stellar mass, SFR, cold-gas surface density, halo mass or specific SFR. CGM attenuation can further reduce escape. | [core/reionization.c][reion-core]: `update_galaxy_fesc_vals()`; `EscapeFracDependency`, `Flag_FescCGMSuppression` |
| [Stellar X-rays](formulas/igm.md#x-ray-propagation-and-deposition) | SFR-dependent emission with a selected normalization, spectrum and energy range; use instantaneous or time-averaged source SFRs. | [ComputeTs.c][thermal], [XRayHeatingFunctions.c][xray]; `LXrayGal`, `SpecIndexXrayGal`, `Flag_InstantaneousSFR` |
| [AGN radiation](formulas/galaxies.md#luminosity-and-escaping-photons) | Accretion supplies ionizing, UV and X-ray emission. The model includes obscuration, duty-cycle weighting and optional randomized accretion onset. | [blackhole_feedback.c][black-holes]: `calculate_BHemissivity()`; `EscapeFracBHNorm`, `Flag_IncludeAGNXray`, `Flag_BHARExponentialCut` |
| [Source scatter](formulas/galaxies.md#scatter-and-escaped-source-budgets) and [median relations](formulas/igm.md#median-source-relation) | Add lognormal escape-fraction or stellar X-ray scatter, or replace source SFRs by median relations at fixed halo mass (noSFR). Optional recalibration restores untreated source budgets. | [Stochasticity.c][stochasticity], [core/reionization.c][reion-core]; `EscapeFracScatterDex`, `XrayScatterDex`, `Flag_RemoveSFRScatter`, `Flag_SourceRecalibration` |
| [Ionized regions](formulas/igm.md#ionization-and-photoheating-feedback) | Filter sources and density on successively smaller scales, comparing the photon supply with hydrogen and recombination requirements. | [find_HII_bubbles.c][ionization]: `find_HII_bubbles()`; `ReionFilterType`, `ReionRBubbleMax` |
| [Recombination sinks](formulas/igm.md#recombination-and-self-shielding) | Track spatially varying recombinations, self-shielding, residual neutral gas and the ionizing background. | [recombinations.c][recombinations], [find_HII_bubbles.c][ionization]; `Flag_IncludeRecombinations`, `Flag_TemperatureDependentRec` |
| [Thermal history](formulas/igm.md#gas-temperature-and-partial-ionization) and [spin temperature](formulas/igm.md#ly-coupling-and-spin-temperature) | Integrate X-ray heating and partial ionization, expansion and Compton terms; calculate collisional and Lyman-alpha coupling of the spin temperature. | [ComputeTs.c][thermal]: `ComputeTs()`; [XRayHeatingFunctions.c][xray]; `Flag_IncludeSpinTemp` |
| [Photoheating feedback](formulas/igm.md#ionization-and-photoheating-feedback) | Use the local ionization history and UV background to set the critical halo mass for gas infall at later snapshots. | [physics/reionization.c][reion-physics]: `calculate_Mvir_crit()`; [core/reionization.c][reion-core]: `assign_Mvir_crit_to_galaxies()` |

[core/reionization.c][reion-core] connects galaxies to the radiation solver:
it updates escape-weighted sources, builds grids, calls the thermal and
ionization routines, assigns feedback to galaxies and writes grid products.
[physics/reionization.c][reion-physics] calculates critical halo masses and
the resulting suppression of gas infall; [find_HII_bubbles.c][ionization]
solves the spatial ionization field.

Source variations alter radiation quantities while retaining the evolving
galaxy reservoirs and star-formation histories. Lognormal scatter preserves
the input median before clipping and generally changes the mean emission.
Recalibration adjusts the deposited budgets; its normalization is described
in [Formulas](formulas/igm.md#source-normalization).

With `Flag_IncludeSpinTemp=1`, the thermal wrapper prepares the source and
density grids before the thermal and ionization calculations. Otherwise,
the ionization wrapper prepares them and the brightness calculation assumes
saturated spin temperature. Updated UVB history enters later snapshots,
closing the feedback loop.

## Observables and saved products

| Product and formulas | Calculation and enabling option | Implementation |
|---|---|---|
| [Galaxy and halo statistics](formulas/numerics.md#distribution-functions) | Save stellar masses, SFRs, gas, metals and black holes; optionally calculate halo and stellar mass functions. | [save.c][save], [dist_func.c][distributions] |
| [Stellar light](formulas/galaxies.md#continuum-filters-and-dust) | With `CALC_MAGS`, combine stellar-population templates with formation histories to obtain intrinsic and dust-attenuated magnitudes in the selected bands. | [magnitudes.c][magnitudes] |
| [Line](formulas/galaxies.md#o-iii-5008-å) and [AGN emission](formulas/galaxies.md#luminosity-and-escaping-photons) | Calculate [O III] emission and quasar luminosities; optional luminosity functions summarize these populations. | [emission_lines.c][lines], [blackhole_feedback.c][black-holes] |
| [21-cm cubes](formulas/igm.md#21-cm-brightness-and-velocities) | `Flag_Compute21cmBrightTemp` combines density, neutral fraction and the chosen spin-temperature treatment; peculiar-velocity effects are optional. | [BrightnessTemperature.c][brightness] |
| [Power spectra and lightcones](formulas/igm.md#global-quantities-power-spectra-and-lightcones) | `Flag_ComputePS` and `Flag_ConstructLightcone` use the brightness field. Both require brightness calculations; lightcones combine the coupled snapshot history. | [ComputePowerSpectrum.c][power], [ConstructLightcone.c][lightcone] |

Selected snapshots write galaxy catalogues and grid products; the master
file links them for analysis. The [output reference](outputs.md) describes
their fields and metadata. [Inputs](inputs.md#model-parameters) lists
model parameters; [Formulas](formulas/index.md) collects the
physical prescriptions.

[main]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/meraxes.c
[params]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/read_params.c
[init]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/init.c
[halos]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/read_halos.c
[loop]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/dracarys.c
[evolve]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/evolve.c
[grids]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/read_grids.c
[reion-core]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/reionization.c
[reion-physics]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/reionization.c
[thermal]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/ComputeTs.c
[ionization]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/find_HII_bubbles.c
[brightness]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/BrightnessTemperature.c
[power]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/ComputePowerSpectrum.c
[lightcone]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/ConstructLightcone.c
[save]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/save.c
[infall]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/infall.c
[cooling]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/cooling.c
[return]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/reincorporation.c
[supernova]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/supernova_feedback.c
[stellar-tables]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/stellar_feedback.c
[star-formation]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/star_formation.c
[black-holes]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/blackhole_feedback.c
[mergers]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/mergers.c
[popiii]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/PopIII.c
[metals]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/metal_evo.c
[xray]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/XRayHeatingFunctions.c
[stochasticity]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/Stochasticity.c
[recombinations]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/recombinations.c
[distributions]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/dist_func.c
[magnitudes]: https://github.com/qyx268/meraxes-devs/blob/forests/src/core/magnitudes.c
[lines]: https://github.com/qyx268/meraxes-devs/blob/forests/src/physics/emission_lines.c
