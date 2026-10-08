# Equation index

The guide contains **211 numbered equation blocks**. Each entry
links to its definition and surrounding variables, units, activation
conditions, source routine and scientific references. A block may contain
several coupled relations. Equations describe the inspected implementation;
paper-only definitions are identified in their corresponding chapter.

## Inputs and configuration

[Read the chapter](inputs.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`run-unit-scales` | Simulation identity, cosmology and units | `run-unit-scales` |
| {eq}`run-galaxy-expansion` | Simulation identity, cosmology and units | `run-galaxy-expansion` |
| {eq}`run-igm-density` | Simulation identity, cosmology and units | `run-igm-density` |
| {eq}`run-igm-expansion` | Simulation identity, cosmology and units | `run-igm-expansion` |
| {eq}`run-cosmic-age` | Simulation identity, cosmology and units | `run-cosmic-age` |
| {eq}`run-input-overdensity` | Density and velocity grids | `run-input-overdensity` |

## Execution workflow

[Read the chapter](workflow.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`run-redshift` | Snapshot time and galaxy timestep | `run-redshift` |
| {eq}`run-lookback` | Snapshot time and galaxy timestep | `run-lookback` |
| {eq}`run-timestep` | Snapshot time and galaxy timestep | `run-timestep` |

## Galaxy formation and evolution

[Read the chapter](galaxy-physics.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`gal-unit-scales` | Units and halo quantities | `gal-unit-scales` |
| {eq}`gal-expansion` | Units and halo quantities | `gal-expansion` |
| {eq}`gal-overdensity` | Units and halo quantities | `gal-overdensity` |
| {eq}`gal-virial-radius` | Units and halo quantities | `gal-virial-radius` |
| {eq}`gal-halo-mass-modifier` | Units and halo quantities | `gal-halo-mass-modifier` |
| {eq}`gal-disk-radius` | Units and halo quantities | `gal-disk-radius` |
| {eq}`gal-virial-temperature` | Units and halo quantities | `gal-virial-temperature` |
| {eq}`gal-temperature-mass` | Units and halo quantities | `gal-temperature-mass` |
| {eq}`gal-evolution-timestep` | Order of operations | `gal-evolution-timestep` |
| {eq}`gal-baryon-budget` | Baryonic infall and stripping | `gal-baryon-budget` |
| {eq}`gal-infall` | Baryonic infall and stripping | `gal-infall` |
| {eq}`gal-baryon-modifier-coordinate` | Baryonic infall and stripping | `gal-baryon-modifier-coordinate` |
| {eq}`gal-modifier-interpolation` | Baryonic infall and stripping | `gal-modifier-interpolation` |
| {eq}`gal-hot-profile` | Atomic cooling | `gal-hot-profile` |
| {eq}`gal-cooling-radius` | Atomic cooling | `gal-cooling-radius` |
| {eq}`gal-cooling-mass` | Atomic cooling | `gal-cooling-mass` |
| {eq}`gal-cooling-transfer` | Atomic cooling | `gal-cooling-transfer` |
| {eq}`gal-molecular-lte` | Molecular cooling in the mini-halo build | `gal-molecular-lte` |
| {eq}`gal-molecular-cooling` | Molecular cooling in the mini-halo build | `gal-molecular-cooling` |
| {eq}`gal-reincorporation-one` | Reincorporation | `gal-reincorporation-one` |
| {eq}`gal-reincorporation-two` | Reincorporation | `gal-reincorporation-two` |
| {eq}`gal-sf-efficiency` | Disk-velocity selector | `gal-sf-efficiency` |
| {eq}`gal-critical-sf` | Prescription 1: critical surface density | `gal-critical-sf` |
| {eq}`gal-pressure-surfaces` | Prescription 2: pressure-dependent molecular gas | `gal-pressure-surfaces` |
| {eq}`gal-pressure-molecular-fraction` | Prescription 2: pressure-dependent molecular gas | `gal-pressure-molecular-fraction` |
| {eq}`gal-pressure-sf-integral` | Prescription 2: pressure-dependent molecular gas | `gal-pressure-sf-integral` |
| {eq}`gal-hydrogen-masses` | Prescription 2: pressure-dependent molecular gas | `gal-hydrogen-masses` |
| {eq}`gal-galform-sf` | Prescription 3: GALFORM-style timescale | `gal-galform-sf` |
| {eq}`gal-sf-reservoir-update` | Formed mass and reservoir update | `gal-sf-reservoir-update` |
| {eq}`gal-metallicity` | Metallicity and feedback tables | `gal-metallicity` |
| {eq}`gal-feedback-kernels` | Metallicity and feedback tables | `gal-feedback-kernels` |
| {eq}`gal-delayed-feedback` | Metallicity and feedback tables | `gal-delayed-feedback` |
| {eq}`gal-feedback-ages` | Metallicity and feedback tables | `gal-feedback-ages` |
| {eq}`gal-ira` | Instantaneous recycling approximation | `gal-ira` |
| {eq}`gal-sn-guo` | Reheating and energy-coupling efficiencies | `gal-sn-guo` |
| {eq}`gal-sn-muratov` | Reheating and energy-coupling efficiencies | `gal-sn-muratov` |
| {eq}`gal-sn-caps` | Reheating and energy-coupling efficiencies | `gal-sn-caps` |
| {eq}`gal-sn-reheating` | Reheating and energy-coupling efficiencies | `gal-sn-reheating` |
| {eq}`gal-sn-energy-host` | Energy-limited reheating and ejection | `gal-sn-energy-host` |
| {eq}`gal-sn-energy-ejection` | Energy-limited reheating and ejection | `gal-sn-energy-ejection` |
| {eq}`gal-sn-availability` | Availability limiter and reservoir update | `gal-sn-availability` |
| {eq}`gal-sn-metal-transfer` | Availability limiter and reservoir update | `gal-sn-metal-transfer` |
| {eq}`gal-popiii-delayed` | Population III conditional extension | `gal-popiii-delayed` |
| {eq}`gal-popiii-current` | Population III conditional extension | `gal-popiii-current` |
| {eq}`gal-popiii-reheat` | Population III conditional extension | `gal-popiii-reheat` |
| {eq}`gal-popiii-energy-conversion` | Population III conditional extension | `gal-popiii-energy-conversion` |
| {eq}`gal-merger-separation` | Dynamical-friction clock | `gal-merger-separation` |
| {eq}`gal-merger-time` | Dynamical-friction clock | `gal-merger-time` |
| {eq}`gal-merger-ratio` | Merger ratio and induced starburst | `gal-merger-ratio` |
| {eq}`gal-merger-burst` | Merger ratio and induced starburst | `gal-merger-burst` |

## Black holes and active galactic nuclei

[Read the chapter](black-holes.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`bh-seed` | Seeding and mergers | `bh-seed` |
| {eq}`bh-hot-accretion` | Hot accretion and radio-mode heating | `bh-hot-accretion` |
| {eq}`bh-hot-cap` | Hot accretion and radio-mode heating | `bh-hot-cap` |
| {eq}`bh-radio-heating` | Hot accretion and radio-mode heating | `bh-radio-heating` |
| {eq}`bh-merger-reservoir` | Merger-fed cold reservoir | `bh-merger-reservoir` |
| {eq}`bh-cold-interval` | Eddington-limited cold accretion and timing | `bh-cold-interval` |
| {eq}`bh-cold-accretion` | Eddington-limited cold accretion and timing | `bh-cold-accretion` |
| {eq}`bh-duration-lbol` | Eddington-limited cold accretion and timing | `bh-duration-lbol` |
| {eq}`bh-bolometric-corrections` | Bolometric corrections and ionizing photons | `bh-bolometric-corrections` |
| {eq}`bh-ionizing-rate` | Bolometric corrections and ionizing photons | `bh-ionizing-rate` |
| {eq}`bh-uv-escape` | Bolometric corrections and ionizing photons | `bh-uv-escape` |
| {eq}`bh-equivalent-sources` | Bolometric corrections and ionizing photons | `bh-equivalent-sources` |
| {eq}`bh-equivalent-stored-increment` | Bolometric corrections and ionizing photons | `bh-equivalent-stored-increment` |
| {eq}`bh-response-weight` | Bolometric corrections and ionizing photons | `bh-response-weight` |
| {eq}`bh-quasar-magnitude` | Bolometric corrections and ionizing photons | `bh-quasar-magnitude` |
| {eq}`bh-obscured-fraction` | X-ray obscuration | `bh-obscured-fraction` |
| {eq}`bh-column-distribution` | X-ray obscuration | `bh-column-distribution` |
| {eq}`bh-xray-transmission` | X-ray obscuration | `bh-xray-transmission` |
| {eq}`bh-photoelectric-cross-section` | X-ray obscuration | `bh-photoelectric-cross-section` |
| {eq}`bh-quasar-heating` | Quasar-mode mechanical feedback | `bh-quasar-heating` |

## Reionization, thermal evolution and the 21-cm signal

[Read the chapter](igm.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`igm-ngp` | Grid assignment and source definitions | `igm-ngp` |
| {eq}`igm-number-densities` | Grid assignment and source definitions | `igm-number-densities` |
| {eq}`igm-stellar-accumulator` | Grid assignment and source definitions | `igm-stellar-accumulator` |
| {eq}`igm-thermal-sfr` | Grid assignment and source definitions | `igm-thermal-sfr` |
| {eq}`igm-filter` | Filter kernels and radius sequence | `igm-filter` |
| {eq}`igm-radius-mass` | Filter kernels and radius sequence | `igm-radius-mass` |
| {eq}`igm-radius-sequence` | Filter kernels and radius sequence | `igm-radius-sequence` |
| {eq}`igm-radius-evolution` | Filter kernels and radius sequence | `igm-radius-evolution` |
| {eq}`igm-efficiency` | Ionizing efficiency and barrier | `igm-efficiency` |
| {eq}`igm-photon-budget` | Ionizing efficiency and barrier | `igm-photon-budget` |
| {eq}`igm-ionization-barrier` | Ionizing efficiency and barrier | `igm-ionization-barrier` |
| {eq}`igm-partial-cell` | Ionizing efficiency and barrier | `igm-partial-cell` |
| {eq}`igm-gamma` | Local ionization rate and intensity | `igm-gamma` |
| {eq}`igm-j21` | Local ionization rate and intensity | `igm-j21` |
| {eq}`igm-critical-mass` | Patchy baryon suppression | `igm-critical-mass` |
| {eq}`igm-baryon-modifier` | Patchy baryon suppression | `igm-baryon-modifier` |
| {eq}`igm-homogeneous-sobacchi` | Homogeneous alternatives | `igm-homogeneous-sobacchi` |
| {eq}`igm-gnedin` | Homogeneous alternatives | `igm-gnedin` |
| {eq}`igm-gnedin-filter` | Homogeneous alternatives | `igm-gnedin-filter` |
| {eq}`igm-mhr-pdf` | Subgrid density distribution | `igm-mhr-pdf` |
| {eq}`igm-effective-redshift` | Subgrid density distribution | `igm-effective-redshift` |
| {eq}`igm-self-shielding` | Self-shielded ionization equilibrium | `igm-self-shielding` |
| {eq}`igm-equilibrium-neutral` | Self-shielded ionization equilibrium | `igm-equilibrium-neutral` |
| {eq}`igm-recombination-integrals` | Self-shielded ionization equilibrium | `igm-recombination-integrals` |
| {eq}`igm-recombination-update` | Self-shielded ionization equilibrium | `igm-recombination-update` |
| {eq}`igm-hmxb-luminosity` | Source spectra and retarded emission | `igm-hmxb-luminosity` |
| {eq}`igm-spectral-normalization` | Source spectra and retarded emission | `igm-spectral-normalization` |
| {eq}`igm-radiation-integral` | Source spectra and retarded emission | `igm-radiation-integral` |
| {eq}`igm-xray-crosssection` | Optical depth and absorption cutoff | `igm-xray-crosssection` |
| {eq}`igm-hydrogenic-crosssection` | Optical depth and absorption cutoff | `igm-hydrogenic-crosssection` |
| {eq}`igm-helium-crosssection` | Optical depth and absorption cutoff | `igm-helium-crosssection` |
| {eq}`igm-xray-optical-depth` | Optical depth and absorption cutoff | `igm-xray-optical-depth` |
| {eq}`igm-xray-kernels` | Heating, ionization and secondary Ly$\alpha$ | `igm-xray-kernels` |
| {eq}`igm-xray-shell-sum` | Heating, ionization and secondary Ly$\alpha$ | `igm-xray-shell-sum` |
| {eq}`igm-thermal-initial` | Initial conditions | `igm-thermal-initial` |
| {eq}`igm-expansion-helpers` | Expansion and growth helpers | `igm-expansion-helpers` |
| {eq}`igm-growth-flat` | Expansion and growth helpers | `igm-growth-flat` |
| {eq}`igm-growth-open` | Expansion and growth helpers | `igm-growth-open` |
| {eq}`igm-electron-evolution` | Governing evolution equations | `igm-electron-evolution` |
| {eq}`igm-temperature-evolution` | Governing evolution equations | `igm-temperature-evolution` |
| {eq}`igm-compton` | Governing evolution equations | `igm-compton` |
| {eq}`igm-compton-fit` | Governing evolution equations | `igm-compton-fit` |
| {eq}`igm-alpha-a` | Governing evolution equations | `igm-alpha-a` |
| {eq}`igm-euler-update` | Discrete update and temperature protection | `igm-euler-update` |
| {eq}`igm-spin-temperature` | Ly$\alpha$ coupling and spin temperature | `igm-spin-temperature` |
| {eq}`igm-collision-coupling` | Ly$\alpha$ coupling and spin temperature | `igm-collision-coupling` |
| {eq}`igm-alpha-coupling` | Ly$\alpha$ coupling and spin temperature | `igm-alpha-coupling` |
| {eq}`igm-stellar-alpha` | Ly$\alpha$ coupling and spin temperature | `igm-stellar-alpha` |
| {eq}`igm-lyman-horizon` | Ly$\alpha$ coupling and spin temperature | `igm-lyman-horizon` |
| {eq}`igm-alpha-correction` | Ly$\alpha$ coupling and spin temperature | `igm-alpha-correction` |
| {eq}`igm-ionized-temperature` | Photoionized-gas temperature | `igm-ionized-temperature` |
| {eq}`igm-partial-temperature` | Photoionized-gas temperature | `igm-partial-temperature` |
| {eq}`igm-lw-band` | Optional minihalo and Lyman–Werner coupling | `igm-lw-band` |
| {eq}`igm-lw-shell` | Optional minihalo and Lyman–Werner coupling | `igm-lw-shell` |
| {eq}`igm-lw-critical-mass` | Optional minihalo and Lyman–Werner coupling | `igm-lw-critical-mass` |
| {eq}`igm-streaming-cooling` | Optional minihalo and Lyman–Werner coupling | `igm-streaming-cooling` |
| {eq}`igm-brightness` | No peculiar velocities | `igm-brightness` |
| {eq}`igm-velocity-thin` | Peculiar-velocity options | `igm-velocity-thin` |
| {eq}`igm-velocity-thick` | Peculiar-velocity options | `igm-velocity-thick` |
| {eq}`igm-rsd-map` | Peculiar-velocity options | `igm-rsd-map` |
| {eq}`igm-grid-averages` | Volume and mass averages | `igm-grid-averages` |
| {eq}`igm-thomson-depth` | Thomson scattering optical depth | `igm-thomson-depth` |
| {eq}`igm-thomson-step` | Thomson scattering optical depth | `igm-thomson-step` |
| {eq}`igm-thomson-post` | Thomson scattering optical depth | `igm-thomson-post` |
| {eq}`igm-ps-fourier` | Fourier normalization and bin averaging | `igm-ps-fourier` |
| {eq}`igm-ps-bins` | Fourier normalization and bin averaging | `igm-ps-bins` |
| {eq}`igm-lightcone-interpolation` | Lightcone construction | `igm-lightcone-interpolation` |

## Stochastic radiation sources

[Read the chapter](stochasticity.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`stoch-fesc-relation` | Deterministic escape fraction | `stoch-fesc-relation` |
| {eq}`stoch-fesc-clamp` | Deterministic escape fraction | `stoch-fesc-clamp` |
| {eq}`stoch-cgm-optical-depth` | Optional CGM attenuation | `stoch-cgm-optical-depth` |
| {eq}`stoch-lognormal` | Escape-fraction scatter and source accumulation | `stoch-lognormal` |
| {eq}`stoch-clipped-mean` | Escape-fraction scatter and source accumulation | `stoch-clipped-mean` |
| {eq}`stoch-source-accumulators` | Escape-fraction scatter and source accumulation | `stoch-source-accumulators` |
| {eq}`stoch-mass-grid` | Distributed median construction | `stoch-mass-grid` |
| {eq}`stoch-sfr-interpolation` | Distributed median construction | `stoch-sfr-interpolation` |
| {eq}`stoch-treated-gsm` | Cumulative treated source history | `stoch-treated-gsm` |
| {eq}`stoch-xray-source-sfr` | Stellar X-ray luminosity scatter | `stoch-xray-source-sfr` |
| {eq}`stoch-xray-luminosity` | Stellar X-ray luminosity scatter | `stoch-xray-luminosity` |
| {eq}`stoch-recalibration` | Snapshot source recalibration | `stoch-recalibration` |

## Population III stars, metal enrichment and synthetic observables

[Read the chapter](optional-physics.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`opt-population-criterion` | Population assignment | `opt-population-criterion` |
| {eq}`opt-popiii-imf` | Pop. III initial mass functions | `opt-popiii-imf` |
| {eq}`opt-popiii-fate-integrals` | Pop. III initial mass functions | `opt-popiii-fate-integrals` |
| {eq}`opt-popiii-lifetime` | Stellar lifetimes and delayed yields | `opt-popiii-lifetime` |
| {eq}`opt-popiii-delay-window` | Stellar lifetimes and delayed yields | `opt-popiii-delay-window` |
| {eq}`opt-popiii-delay-fractions` | Stellar lifetimes and delayed yields | `opt-popiii-delay-fractions` |
| {eq}`opt-streaming-cooling` | Streaming velocities and LW cooling threshold | `opt-streaming-cooling` |
| {eq}`opt-molecular-virial-mass` | Streaming velocities and LW cooling threshold | `opt-molecular-virial-mass` |
| {eq}`opt-lw-mass-threshold` | Streaming velocities and LW cooling threshold | `opt-lw-mass-threshold` |
| {eq}`opt-metal-bubble` | Supernova-driven metal bubbles | `opt-metal-bubble` |
| {eq}`opt-metal-ambient-density` | Supernova-driven metal bubbles | `opt-metal-ambient-density` |
| {eq}`opt-enrichment-probability` | Deposition, enrichment probability and infall metallicity | `opt-enrichment-probability` |
| {eq}`opt-cell-metallicity` | Deposition, enrichment probability and infall metallicity | `opt-cell-metallicity` |
| {eq}`opt-unused-clustering-fit` | Deposition, enrichment probability and infall metallicity | `opt-unused-clustering-fit` |
| {eq}`opt-sed-convolution` | Stellar continuum and dust | `opt-sed-convolution` |
| {eq}`opt-sector-rest-filter` | Stellar continuum and dust | `opt-sector-rest-filter` |
| {eq}`opt-sector-observer-filter` | Stellar continuum and dust | `opt-sector-observer-filter` |
| {eq}`opt-dust-normalization` | Stellar continuum and dust | `opt-dust-normalization` |
| {eq}`opt-sector-dust-attenuation` | Stellar continuum and dust | `opt-sector-dust-attenuation` |
| {eq}`opt-ab-magnitude` | Stellar continuum and dust | `opt-ab-magnitude` |
| {eq}`opt-oiii-collision` | Collision coefficients | `opt-oiii-collision` |
| {eq}`opt-oiii-bubble-radius` | Disk, turbulent support and source bubbles | `opt-oiii-bubble-radius` |
| {eq}`opt-oiii-disk-support` | Disk, turbulent support and source bubbles | `opt-oiii-disk-support` |
| {eq}`opt-oiii-stromgren` | Disk, turbulent support and source bubbles | `opt-oiii-stromgren` |
| {eq}`opt-oiii-luminosity` | Luminosity and dust | `opt-oiii-luminosity` |
| {eq}`opt-oiii-dust` | Luminosity and dust | `opt-oiii-dust` |

## Numerical conventions and parallel execution

[Read the chapter](numerics.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`num-derived-units` | Unit scales and powers of the Hubble parameter | `num-derived-units` |
| {eq}`num-rate-output` | Rates and output metadata | `num-rate-output` |
| {eq}`num-hubble-unit` | Rates and output metadata | `num-hubble-unit` |
| {eq}`num-cell-size` | Coordinates, periodic boundaries and cell assignment | `num-cell-size` |
| {eq}`num-ngp-index` | Coordinates, periodic boundaries and cell assignment | `num-ngp-index` |
| {eq}`num-ngp-source` | Coordinates, periodic boundaries and cell assignment | `num-ngp-source` |
| {eq}`num-grid-resample` | Density-grid preparation | `num-grid-resample` |
| {eq}`num-density-normalisation` | Density-grid preparation | `num-density-normalisation` |
| {eq}`num-grid-layout` | Real, padded and complex array layouts | `num-grid-layout` |
| {eq}`num-special-layouts` | Real, padded and complex array layouts | `num-special-layouts` |
| {eq}`num-fft-normalisation` | Fourier transforms and smoothing | `num-fft-normalisation` |
| {eq}`num-fft-wavevectors` | Fourier transforms and smoothing | `num-fft-wavevectors` |
| {eq}`num-filter-windows` | Fourier transforms and smoothing | `num-filter-windows` |
| {eq}`num-forest-load` | Forest ownership for galaxies | `num-forest-load` |
| {eq}`num-forest-capacity` | Forest ownership for galaxies | `num-forest-capacity` |
| {eq}`num-slab-ownership` | Slab ownership for grids | `num-slab-ownership` |
| {eq}`num-lookback-time` | Snapshot time and finite histories | `num-lookback-time` |
| {eq}`num-thermal-update` | Thermal update and lightcone time | `num-thermal-update` |
| {eq}`num-cosmic-time-helper` | Thermal update and lightcone time | `num-cosmic-time-helper` |
| {eq}`num-table-integration` | Precision and reproducibility | `num-table-integration` |
| {eq}`num-close-tolerance` | Precision and reproducibility | `num-close-tolerance` |
| {eq}`num-resolution-scales` | Resolution and resource scaling | `num-resolution-scales` |
| {eq}`num-grid-memory` | Resolution and resource scaling | `num-grid-memory` |
| {eq}`num-galaxy-memory` | Resolution and resource scaling | `num-galaxy-memory` |

## Output files and data dictionary

[Read the chapter](outputs.md).

| Equation | Process | Identifier |
|---|---|---|
| {eq}`out-df-bins` | Mass and luminosity functions | `out-df-bins` |
| {eq}`out-df-density` | Mass and luminosity functions | `out-df-density` |
| {eq}`out-df-uncertainty` | Mass and luminosity functions | `out-df-uncertainty` |
