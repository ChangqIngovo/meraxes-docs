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

| Stage | Main routines | Operation |
|---|---|---|
| Launch | `main()` | Initialize MPI. |
| Configure | `read_parameter_file()` | Read run, simulation and default parameters. |
| Initialize | `init_meraxes()`, `init_storage()` | Load snapshot times and physical tables; allocate galaxy and grid storage. |
| Read halos | `read_halos()` and host bookkeeping | Connect galaxies to descendants, initialize new galaxies and sample stored UVB feedback. |
| Evolve galaxies | `evolve_galaxies()` | Update gas, stars, metals, black holes and mergers. |
| Prepare grids | `construct_baryon_grids()`, `read_grid()` | Deposit galaxy sources and read simulation density. |
| Evolve the IGM | `ComputeTs()`, `find_HII_bubbles()` | Calculate enabled thermal fields, ionization and UVB history. |
| Calculate observables | `ComputeBrightnessTemperatureBox()`, `Compute_PS()`, `ConstructLightcone()` | Produce requested 21-cm brightness, power spectra and lightcones. |
| Save snapshot | `write_snapshot()` and grid writers | Save selected galaxy catalogues and grid products; advance the loop. |
| Finish | `create_master_file()` | Assemble links to rank files and grid files after the final snapshot. |

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

| Process | Physical role and model choices | Main routines / controls |
|---|---|---|
| Infall | Supply the central galaxy according to the halo baryon budget, reduced by photoheating. | `gas_infall()`, `reionization_modifier()` |
| Cooling and return | Cool hot gas onto the central galaxy using temperature- and metallicity-dependent rates; return ejected material to the hot reservoir. | `gas_cooling()`, `reincorporate_ejected_gas()`; `ReincorporationModel` |
| Stellar returns | Earlier stellar populations return gas, newly formed metals and supernova energy on their stellar-evolution timescales. Instantaneous recycling is an alternative. | `delayed_supernova_feedback()`; `Flag_IRA` |
| Star formation | Convert cold gas into stars using a critical-density law, a pressure-dependent molecular-gas law, or a dynamical-timescale law. | `insitu_star_formation()`; `SfPrescription=1`, `2`, or `3` |
| Supernova feedback | Reheat cold gas and eject halo gas according to the available energy and halo potential; update metal reservoirs. | `contemporaneous_supernova_feedback()`; `SnModel` |
| Black-hole growth | Accrete hot gas and consume a cold-gas reservoir supplied by mergers. Radio-mode heating reduces cooling; quasar-mode feedback reheats or ejects gas. | `radio_mode_BH_heating()`, `previous_merger_driven_BH_growth()` |
| Galaxy mergers | Merge reservoirs and stellar histories when an orphan's merger clock expires; eligible mergers trigger a starburst and feed the black-hole accretion reservoir. | `merge_with_target()`; `MergerTimeFactor`, burst parameters |

Cooling is evaluated before adding the current infall and reincorporated gas.
Delayed returns and previously queued black-hole accretion precede new star
formation; mergers follow this evolution. This order determines which gas
and feedback contributions are available during the current step.

With `USE_MINI_HALOS`, molecular cooling extends star formation into smaller
halos, and metallicity selects Pop. III or Pop. II star formation. Optional
Lyman–Werner radiation, streaming velocities and external enrichment modify
the onset of this activity. These additions share the same reservoir and
source-processing sequence.

## Radiation and feedback

Source deposition sums galaxy contributions in their nearest grid cells.
The `stars` grid stores an escaped cumulative stellar-source quantity;
`weighted_sfr` supplies the corresponding current source rate. Black holes
contribute through separate effective source grids. These fields pass to the
radiation solver after deposition.

| Component | Model treatment | Main controls |
|---|---|---|
| Stellar ionizing emission | Escape fractions may depend on redshift, stellar mass, SFR, cold-gas surface density, halo mass or specific SFR. CGM attenuation can further reduce escape. | `EscapeFracDependency`, `Flag_FescCGMSuppression` |
| Stellar X-rays | SFR-dependent emission with a selected normalization, spectrum and energy range; use instantaneous or time-averaged source SFRs. | `LXrayGal`, `SpecIndexXrayGal`, `Flag_InstantaneousSFR` |
| AGN radiation | Accretion supplies ionizing, UV and X-ray emission. The model includes obscuration, duty-cycle weighting and optional randomized accretion onset. | `EscapeFracBHNorm`, `Flag_IncludeAGNXray`, `Flag_BHARExponentialCut` |
| Source variations | Add lognormal escape-fraction or stellar X-ray scatter, or replace source SFRs by median relations at fixed halo mass (noSFR). Optional recalibration restores untreated source budgets. | `EscapeFracScatterDex`, `XrayScatterDex`, `Flag_RemoveSFRScatter`, `Flag_SourceRecalibration` |
| Ionized regions | Filter sources and density on successively smaller scales, comparing the photon supply with hydrogen and recombination requirements. | `find_HII_bubbles()`; `ReionFilterType`, `ReionRBubbleMax` |
| Recombination sinks | Track spatially varying recombinations, self-shielding, residual neutral gas and the ionizing background. | `Flag_IncludeRecombinations`, `Flag_TemperatureDependentRec` |
| Thermal history | Integrate X-ray heating and partial ionization, expansion and Compton terms; calculate collisional and Lyman-alpha coupling of the spin temperature. | `ComputeTs()`; `Flag_IncludeSpinTemp` |
| Photoheating feedback | Use the local ionization history and UV background to set the critical halo mass for gas infall at later snapshots. | `calculate_Mvir_crit()`, `assign_Mvir_crit_to_galaxies()` |

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

| Product | Calculation and enabling option |
|---|---|
| Galaxy and halo statistics | Save stellar masses, SFRs, gas, metals and black holes; optionally calculate halo and stellar mass functions. |
| Stellar light | With `CALC_MAGS`, combine stellar-population templates with formation histories to obtain intrinsic and dust-attenuated magnitudes in the selected bands. |
| Line and AGN emission | Calculate [O III] emission and quasar luminosities; optional luminosity functions summarize these populations. |
| 21-cm cubes | `Flag_Compute21cmBrightTemp` combines density, neutral fraction and the chosen spin-temperature treatment; peculiar-velocity effects are optional. |
| Power spectra and lightcones | `Flag_ComputePS` and `Flag_ConstructLightcone` use the brightness field. Both require brightness calculations; lightcones combine the coupled snapshot history. |

Selected snapshots write galaxy catalogues and grid products; the master
file links them for analysis. The [output reference](outputs.md) describes
their fields and metadata. [Inputs](inputs.md#feature-combinations) lists
compatible feature combinations; [Formulas](formulas/index.md) collects the
physical prescriptions.
