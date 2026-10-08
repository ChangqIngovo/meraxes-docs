# Inputs and configuration

A Meraxes run combines three kinds of input: halo histories and simulation
fields, physical lookup tables, and a parameter hierarchy. All file formats and
parameter names below describe the pinned `forests` source. The numerical
prescriptions are documented in [Galaxy physics](galaxy-physics.md),
[Black holes](black-holes.md), [IGM](igm.md) and [Stochasticity](stochasticity.md).

## Parameter files and precedence

Parameter files use `Name : value` entries with `#` comments. Names are
case-sensitive and paths are literal strings. The reader assigns a parameter
only once, so the priority is:

1. The parameter file supplied on the command line.
2. `SimParamsFile`, if supplied.
3. `DefaultsFile`.

The **first occurrence also wins within a file**. An unrecognized name aborts,
even though the diagnostic is labeled a warning; missing required parameters
also abort. Use top-level entries as in the supplied templates. The source
`input/params/input.par` contains CMake substitution tokens; build configuration
creates a usable `build/input.par`. Relative runtime paths are resolved from the
process's working directory, not from the parameter file's directory.

The atlas below covers all **221 unique registered names**. Defaults are the
values in the pinned `input/params/defaults.par`, not a recommended scientific
calibration: a simulation file can override them. A blank default means an
empty string. Parameters without a simulation-independent default must be
provided through the user or simulation file when required.

Source: [parameter registry and checks](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_params.c),
[parser](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/parse_paramfile.c) and
[default file](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/input/params/defaults.par).

### File and output configuration

| Parameter | Default / requirement | Meaning |
|---|---|---|
| `DefaultsFile` | Required | Simulation-independent default parameter file. |
| `SimParamsFile` | Empty / optional | Simulation-specific parameters, including data locations and cosmology. |
| `SimulationDir` | Required | Root containing `a_list.txt`, trees, catalogues and simulation grids. |
| `CatalogFilePrefix` | Required | Catalogue/tree basename interpreted by the selected reader. |
| `CoolingFuncsDir` | Required | Directory containing `SD93.hdf5`. |
| `StellarFeedbackDir` | Required | Directory containing `stellar_feedback_tables.hdf5`; the shipped template selects `Kroupa`. |
| `TablesForXHeatingDir` | Required registry entry | Directory of thermal/radiative tables; used by the heating/spin-temperature path. |
| `RecombinationDir` | Optional registry entry | Cache directory for recombination interpolation tables; supply it when enabling recombinations. |
| `PhotometricTablesDir` | Required with `CALC_MAGS` | Directory of the stellar SED library and enabled observed filters. |
| `FileNameGalaxies` | Required | Output basename; the template uses `meraxes`. |
| `OutputDir` | Required | Output directory. Pre-create its parents if using a nested path. |
| `OutputSnapshots` | Required | Selected snapshot indices or ranges; the loop still evolves intermediate snapshots. |
| `FFTW3WisdomDir` | Empty / optional | Directory for FFTW planning wisdom. |

`OutputSnapshots : :` selects the full snapshot list; `-1` selects the last
snapshot; `100:110,-5:` selects indices 100–109 and the last five snapshots.
Ranges have an exclusive upper bound. Use individual indices and two-endpoint
ranges: the current parser counts a third slice field but does not honor its
stride when filling the list. Keep indices within `a_list.txt` and select a
final output snapshot greater than 1, as required by stellar-feedback history
initialization. Magnitude builds must also align `TargetSnaps` and compile-time
`MAGS_N_SNAPS` with the intended saved snapshots.

### Simulation identity, cosmology and units

These have no simulation-independent defaults. The values must describe the
same simulation as the trees and grids.

| Parameter | Meaning / convention |
|---|---|
| `SimName` | Descriptive simulation name. |
| `TreesID` | `0`: VELOCIraptor; `1`: gbpTrees; `2`: augmented VELOCIraptor. |
| `BoxSize` | Comoving box side; supplied simulations use $h^{-1}\,\mathrm{Mpc}$. |
| `PartMass` | Dark-matter particle mass in internal mass units. |
| `NPart` | Total simulation particle count; registered as a 64-bit integer. |
| `Hubble_h` | $H_0/(100\,\mathrm{km\,s^{-1}\,Mpc^{-1}})$. |
| `BaryonFrac` | Universal baryon-to-total-matter mass fraction, $\Omega_b/\Omega_m$. |
| `OmegaM` | Present matter density parameter. |
| `OmegaK` | Curvature parameter used by the galaxy virial/time routines. |
| `OmegaR` | Radiation parameter used by the IGM Hubble/growth routines. |
| `OmegaLambda` | Cosmological-constant density parameter. |
| `Sigma8` | Simulation fluctuation normalization retained in the parameter record. |
| `SpectralIndex` | Primordial spectral index retained in the parameter record. |
| `wLambda` | Dark-energy equation-of-state parameter read by the IGM growth helper; this is not general support for arbitrary $w$ in every cosmological routine. |
| `UnitLength_in_cm` | Numerical cgs length scale; standard value $3.08568\times10^{24}$ for Mpc-based units. |
| `UnitMass_in_g` | Numerical cgs mass scale; standard value $1.989\times10^{43}$ for $10^{10}M_\odot$-based units. |
| `UnitVelocity_in_cm_per_s` | Numerical cgs velocity scale; standard value $10^5$ for km s$^{-1}$. |

The supplied simulation files use internal mass $10^{10}h^{-1}M_\odot$, length
$h^{-1}\mathrm{Mpc}$ and velocity km s$^{-1}$. Their numerical cgs scales are
stored separately from the little-$h$ factor. Initialization constructs

```{math}
:label: run-unit-scales
U_t=\frac{U_L}{U_v},\qquad
U_\rho=\frac{U_M}{U_L^3},\qquad
U_E=U_M U_v^2,\qquad
G_{\rm int}=G_{\rm cgs}\frac{U_M U_t^2}{U_L^3}.
```

For these supplied conventions, physical mass and length are an internal value
times $U_M/h$ and $U_L/h$, physical time is times $U_t/h$, and physical density
is times $U_\rho h^2$. Position fields in the input/output catalogues require
additional attention to comoving versus proper coordinates; see the reader
conversions below and [Outputs](outputs.md).

The galaxy virial routines use

```{math}
:label: run-galaxy-expansion
E_{\rm gal}(z)=
\sqrt{\Omega_m(1+z)^3+\Omega_k(1+z)^2+\Omega_\Lambda},\qquad
H_{\rm gal,int}(z)=H_{100}U_t E_{\rm gal}(z),\qquad
\rho_{\rm crit,int}(z)=\frac{3H_{\rm gal,int}^2(z)}{8\pi G_{\rm int}},
```

where $H_{100}=100\,\mathrm{km\,s^{-1}\,Mpc^{-1}}$. IGM density constants use
physical $H_0=hH_{100}$ instead:

```{math}
:label: run-igm-density
\rho_{\rm crit,0}=\frac{3(hH_{100})^2}{8\pi G},\qquad
\Omega_b=f_b\Omega_m,\qquad
\bar n_{\rm H,0}=\frac{\rho_{\rm crit,0}\Omega_b(1-Y_{\rm He})}{m_p},\qquad
\bar n_{\rm He,0}=\frac{\rho_{\rm crit,0}\Omega_bY_{\rm He}}{4m_p}.
```

The IGM helpers use

```{math}
:label: run-igm-expansion
H_{\rm IGM}(z)=hH_{100}
\sqrt{\Omega_m(1+z)^3+\Omega_R(1+z)^4+\Omega_\Lambda},
```

and the analytic cosmic-age expression

```{math}
:label: run-cosmic-age
t_{\rm age}(z)=
\frac{2\sqrt{1+\Omega_m/\Omega_\Lambda}}{3hH_{100}}
\operatorname{asinh}\!\left[
\sqrt{\frac{\Omega_\Lambda}{\Omega_m}}(1+z)^{-3/2}
\right].
```

The age helper assumes a flat matter–$\Lambda$ cosmology and contains no
radiation term. The IGM Hubble helper omits curvature, and the galaxy
lookback-time integrator omits radiation. These implemented conventions matter
when changing cosmology beyond the supplied standard flat-$\Lambda$ setups.
See [Workflow](workflow.md) for the actual galaxy timestep.

Source: [unit initialization](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/init.c),
[virial cosmology](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/virial_properties.c),
[IGM density definitions](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.h) and
[IGM time/Hubble helpers](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/XRayHeatingFunctions.c).

## Halo histories and grid inputs

### Snapshot list and trees

`<SimulationDir>/a_list.txt` is a whitespace-separated sequence of expansion
factors $a$, in snapshot order. It is not a redshift list. The list length sets
valid snapshot indices and the required lengths of precomputed critical-mass
histories.

| `TreesID` | Required tree locations |
|---|---|
| `0` | `trees/<CatalogFilePrefix>` and `trees/meraxes_augmented_stats.h5`. |
| `1` | `trees/horizontal_trees_%03d.hdf5`, `trees/forests_info.hdf5`, and group/subgroup property catalogues under `catalogs/`. |
| `2` | `augmented_trees/<CatalogFilePrefix>` and `augmented_trees/meraxes_augmented_stats.h5`. |

Paths in this table are relative to `SimulationDir`; `%03d` is a zero-padded
snapshot number. For VELOCIraptor, the reader expects `Snap_%03d` groups,
`NHalos` and `scalefactor` attributes, the `Header/Units` mass-conversion
attribute, and `ForestID`, `Head`, `hostHaloID`, `Mass_200crit`, `Mass_tot`,
`R_200crit`, `Vmax`, position, velocity, angular-momentum, `ID` and `npart`
datasets. Hosts must precede their subhalos.

For gbpTrees, each of `groups` and `subgroups` property catalogues is searched
in the following order. Let `P` be `CatalogFilePrefix`, `S` the three-digit
snapshot and `T` the catalogue type:

1. `catalogs/P_S.catalog_T_properties/P_S.catalog_T_properties.i`
2. `catalogs/P_S.catalog_T_properties/P_S.catalog_T_properties`
3. `catalogs/P_S.catalog_T_properties.i`
4. `catalogs/P_S.catalog_T_properties`

The split-file index `i` begins at 0. Catalogue readers apply different source
conventions:

| Reader | Conversion to Meraxes quantities |
|---|---|
| gbpTrees | FoF catalogue mass in $M_\odot/h$ is divided by $10^{10}$; catalogue positions/radii use Mpc/$h$, velocities km s$^{-1}$. Subhalo mass/radius can be reconstructed from particle count and virial relations. |
| VELOCIraptor | Mass is multiplied by $h\,\mathrm{Mass\_unit\_to\_solarmass}/10^{10}$; positions by $h/a$ and wrapped periodically; velocities divided by $a$; radii and angular momentum multiplied by $h$; `Vmax` is unchanged. Halo mass uses `Mass_tot`; central FoF mass normally uses `Mass_200crit`, with `Mass_tot` as fallback. |

Source: [reader dispatch/forest selection](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos.c),
[gbpTrees](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos-gbptrees.c) and
[VELOCIraptor](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos-velociraptor.c).

### Density and velocity grids

The radiation calculation reads simulation **density**, then converts it into
an overdensity. Grid dimensions must match the reader's cubic-box layout;
the input resolution must be at least `ReionGridDim` and divisible by it.
Higher-resolution fields are smoothed and downsampled. Readers apply no
additional velocity-unit conversion, so use the conventions expected by the
simulation-grid producer.

| Format | Filename and field layout |
|---|---|
| SWIFT HDF5 | `grids/snap_%04d.hdf5`; datasets `/PartType1/Grids/{Density,Vx,Vy,Vz}` and `/Header` attribute `BoxSize`. |
| Postprocessed VELOCIraptor | `grids/snapshot_%03d.den.i` and `grids/snapshot_%03d.vel.i`; root datasets `Density`, `Vx`, `Vy`, `Vz`, and attributes `Num_files`, `BoxSize`, `Ngrid_X/Y/Z`, `Local_x_start`, `Local_nx`. |
| gbpTrees binary | `grids/snapshot_%03d_dark_grid.dat`; native binary header with grid dimensions, box size, grid count and assignment scheme, then four float fields with 32-byte identifiers: density first, then the velocity components. |

For VELOCIraptor tree modes, format detection first probes the unresampled
SWIFT file, then `grids/snapshot_%03d.den.0`. If the directory
`grids/resampled/N<ReionGridDim>` exists, the SWIFT and gbpTrees readers choose
its corresponding snapshot file. This is a directory-level choice: there is
no per-snapshot fallback to the unresampled file. A resampled-only SWIFT input
also fails the initial format probe. Density must be read first for the
postprocessed format because velocity files may omit `Num_files`.

The implemented normalization is

```{math}
:label: run-input-overdensity
\delta(\mathbf{x})=
\rho_{\rm file}(\mathbf{x})
\frac{L_{\rm file}^{3}h}{N_{\rm part}M_{\rm part}}-1,
```

with a numerical floor at or just above $-1$, depending on the reader. Here
$L_{\rm file}$ is the box side read from the grid header and $M_{\rm part}$ is
`PartMass`. The source explicitly includes the additional $h$ factor to
compensate its input-grid unit convention. An already normalized overdensity
field therefore cannot be substituted for the expected density dataset.

Velocity is loaded by `call_ComputeTs()` when `Flag_IncludePecVelsFor21cm>0`;
the brightness routine applies its velocity treatment only when spin-temperature
calculations are also enabled. At that stage it converts gbpTrees velocities
by $v_{\rm proper}=\sqrt{a}\,v_{\rm file}/1000$ and VELOCIraptor/SWIFT velocities
by $v_{\rm proper}=v_{\rm file}/a$, targeting physical km s$^{-1}$. These
conversions are distinct from the halo-catalogue velocity conversion.
See [IGM](igm.md) for flag dependencies and
velocity-gradient/RSD prescriptions.

Source: [grid dispatch/resampling](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids.c),
[SWIFT and VELOCIraptor grids](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids-velociraptor.c),
[gbpTrees grids](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids-gbptrees.c),
[brightness velocity conversions](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/BrightnessTemperature.c),
[solver wrappers](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c).

## Physical tables and optional histories

| Parameter / location | Loaded content and condition |
|---|---|
| `CoolingFuncsDir/SD93.hdf5` | Always loaded: eight metallicity groups `mzero`, `m-30`, `m-20`, `m-15`, `m-10`, `m-05`, `m-00`, `m+05`, each containing `log(lambda_norm)`. |
| `StellarFeedbackDir/stellar_feedback_tables.hdf5` | Always loaded: `age`, `total_yield`, `total_metal_yield`, `energy`; ages are Myr, yield rates Myr$^{-1}$, and energy is converted using the internal energy scale. |
| `TablesForXHeatingDir` | Heating/spin-temperature path: `recfast_LCDM.dat`, `stellar_spectra.dat`, `kappa_eH_table.dat`, `kappa_pH_table.dat`, plus secondary-ionization tables under `x_int_tables/`. |
| `PhotometricTablesDir/sed_library.hdf5` | Stellar SED library for `CALC_MAGS`. |
| `PhotometricTablesDir/NIRCam_Wide/` and `HST_IR/` | Enabled observed filters: paired `FxxxW_wavelength.bin` and `FxxxW_transmission.bin`. |
| Pop. III photometric library | With minihalos and magnitudes, `PopIII_IMF` selects `Sal500_001.hdf5`, `Sal500_050.hdf5`, `logA500_001.hdf5` or `logE500_001.hdf5` in `PhotometricTablesDir`. |
| `MvirCritFile` | With `Flag_ReionizationModifier=3`, HDF5 dataset `mean_Mvir_crit`, one internal-mass value per snapshot. |
| `MvirCritMCFile` | Minihalo counterpart, dataset `mean_Mvir_crit_MC`, with the same required list length. |
| `MassRatioModifier` / `BaryonFracModifier` | Optional HDF5 correction tables named `%03d` by snapshot; read mass-bin bounds and the relevant ratio fields. |
| `RecombinationDir` | Optional interpolation cache used when recombinations are enabled; missing caches are recomputed. |

The secondary-ionization files are `log_xi_-4.0.dat`, `log_xi_-3.6.dat`,
`log_xi_-3.3.dat`, `log_xi_-3.0.dat`, `log_xi_-2.6.dat`, `log_xi_-2.3.dat`,
`log_xi_-2.0.dat`, `log_xi_-1.6.dat`, `log_xi_-1.3.dat`, `log_xi_-1.0.dat`,
`xi_0.500.dat`, `xi_0.900.dat`, `xi_0.990.dat`, and `xi_0.999.dat`.

The recombination cache consists of native double arrays in
`lnGamma_table_-10-150-0.1.bin`,
`RR_table_-10-150-0.1_0-200-0.2_2-100-0.03.bin`, and matching `CF_table` and
`RNH_table` filenames. If any is missing, the code regenerates all four and
attempts to write them. Verify file presence and schema before a run; several
physical-table readers have limited file-open/schema diagnostics.

The correction-table reader expects 31 records per snapshot table. Its common
fields are `log10(mass_lower)`, `log10(mass_upper)`, `mass_mean`, `mass_errl`
and `mass_erru`; the mass-ratio file adds `ratio_mean`, `ratio_errl`,
`ratio_erru`, while the baryon-fraction file adds `fb_mean`, `fb_errl`,
`fb_erru`. The interpolation coordinate is $\log_{10}(M/M_\odot)$, evaluated
from the uncorrected FoF mass; the knots are `log10(mass_lower) + 0.5`.
The reader applies no field-unit conversion. These corrections derive from
the halo-growth treatment of
[Qin et al. (2017)](https://doi.org/10.1093/mnras/stx083).
Critical-mass history datasets are also consumed directly without a mass-unit
conversion.

Source: [cooling tables](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/cooling.c),
[stellar tables](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/stellar_feedback.c),
[heating tables](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/XRayHeatingFunctions.c),
[photometry](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/magnitudes.c),
[critical-mass histories](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization_modifiers.c),
[correction tables](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/modifiers.c),
[recombination caches](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/recombinations.c).

### Optional selection and correction parameters

| Parameter | Default | Meaning |
|---|---|---|
| `ForestIDFile` | Empty | Text file containing a forest count, followed by one forest ID per line. |
| `MvirCritFile` | Empty | Precomputed UVB infall-suppression critical-mass history. |
| `MvirCritMCFile` | Empty | Precomputed molecular-cooling/minihalo critical-mass history. |
| `MassRatioModifier` | Empty | Halo-mass correction table path. |
| `BaryonFracModifier` | Empty | Halo baryon-fraction correction table path. |
| `Flag_BHObscuedIonization` | Not set in `defaults.par` | Registered legacy spelling; the global structure starts at zero, and the present production BH ionizing-emissivity routine does not consult this flag. |

`ForestIDFile` is explicitly marked poorly tested in the source. Its MPI reader
mixes `long` storage with an `MPI_INT` broadcast. The correction-table readers
broadcast `sizeof(pointer)` bytes rather than the full allocated table. These
optional paths need correction or explicit multi-rank validation before use;
the default empty paths avoid them.

## Runtime parameter atlas

The following tables reproduce every unique key and value in `defaults.par`.
The preceding tables account for all remaining registered names. Suffix `_III`
and the named Pop. III controls refer to mini-halo builds; the parser accepts
many of these names without that feature, but the relevant physics is compiled
conditionally. Photometry requires `CALC_MAGS`; scatter/no-SFR/recalibration
requires `USE_STOCHASTICITY`.

### Execution controls

| Parameter | Default | Meaning / units |
|---|---|---|
| `NSteps` | `1` | Galaxy substeps; must equal 1 in this version. |
| `FlagInteractive` | `0` | 0: standard; 1: interactive/cached; 2: distribution functions without galaxy-record writes. |
| `FlagSubhaloVirialProps` | `0` | Select catalogue virial properties versus particle-count approximations for subhalos. |
| `FlagMCMC` | `0` | External MCMC integration mode; suppress ordinary output writes. |
| `FlagIgnoreProgIndex` | `0` | Skip progenitor-index tracking when requested. |
| `RandomSeed` | `1809` | Seed for the GSL random generator. |
| `VolumeFactor` | `1.0` | Effective-volume correction for subsampled trees; use the matching selection convention. |

### Radiation execution flags

| Parameter | Default | Meaning / units |
|---|---|---|
| `Flag_IncludeRecombinations` | `0` | Enable inhomogeneous hydrogen recombinations. |
| `Flag_EvolvingReionRBubbleMax` | `1` | Use the evolving maximum bubble-radius prescription instead of the fixed-radius controls. |
| `Flag_TemperatureDependentRec` | `1` | Use temperature-dependent recombination calculations when recombinations are enabled. |
| `Flag_Compute21cmBrightTemp` | `0` | Compute coeval 21-cm brightness temperature. |
| `Flag_ComputePS` | `0` | Compute the coeval 21-cm power spectrum; also request brightness calculation. |
| `Flag_IncludeSpinTemp` | `0` | Compute thermal and spin-temperature fields; 0 uses the saturated-spin-temperature approximation. |
| `Flag_InstantaneousSFR` | `1` | Use instantaneous rather than the legacy smoothed SFR in X-ray source calculations. |
| `Flag_IncludePecVelsFor21cm` | `0` | 0: none; 1: capped velocity gradient; 2: uncapped gradient; 3: uncapped gradient plus RSD remapping. The path also requires spin-temperature calculations. |
| `Flag_ConstructLightcone` | `0` | Construct the brightness lightcone; requires a consistent coupled brightness history. |
| `Flag_IncludeLymanWerner` | `0` | Minihalo Lyman–Werner radiation feedback. |
| `Flag_IncludeMetalEvo` | `0` | Minihalo external IGM metal-enrichment calculation. |
| `Flag_IncludeStreamVel` | `0` | Minihalo baryon–dark-matter streaming-velocity treatment. |
| `Flag_RemoveSFRScatter` | `0` | Enable the deterministic no-SFR source prescription; see Stochasticity. |

### Minihalo and external metal-enrichment controls

Minihalo/Pop. III terms are conditional on `USE_MINI_HALOS`; see [Galaxy physics](galaxy-physics.md).

| Parameter | Default | Meaning / units |
|---|---|---|
| `MetalGridDim` | `128` | Cells per side of the external-metal grid. |
| `AlphaCluster` | `-1.4` | Nonlinear-clustering fit coefficient; source-default comments mark this fit inactive in the present implementation. |
| `BetaCluster` | `0.8` | Nonlinear-clustering fit coefficient; same qualification as AlphaCluster. |
| `GammaCluster` | `2.8` | Nonlinear-clustering fit coefficient; same qualification as AlphaCluster. |
| `NormCluster` | `200.0` | Nonlinear-clustering fit normalization; same qualification as AlphaCluster. |
| `ZCrit` | `0.0001` | Pop. II is selected when the cold-gas metal mass fraction divided by `0.01` exceeds this value; the default absolute threshold is `1e-6`. |

### X-ray luminosity and AGN spectral controls

See [Black holes](black-holes.md), [IGM](igm.md) and [Stochasticity](stochasticity.md) for the source formulas and applicability.

| Parameter | Default | Meaning / units |
|---|---|---|
| `LXrayGal` | `3.16e40` | Galaxy soft-band luminosity per SFR, (erg s⁻¹)/(M☉ yr⁻¹). |
| `XrayScatterDex` | `0.0` | Scatter in log10 galaxy X-ray luminosity at fixed SFR, dex. |
| `LXrayGalIII` | `3.16e40` | Pop. III counterpart of LXrayGal, in the same units. |
| `SpecIndexXrayGal` | `1.` | Galaxy X-ray spectral index α in Lν ∝ ν⁻α. |
| `SpecIndexXrayIII` | `1.` | Pop. III X-ray spectral index. |
| `NuXrayThreshold` | `500.` | Lower escaping X-ray photon energy, eV. |
| `NuXraySoftCut` | `2000.` | Soft/hard X-ray break or upper soft-band energy, eV. |
| `NuXrayMax` | `10000.` | Upper X-ray integration energy, eV. |
| `Flag_IncludeAGNXray` | `0` | 0: no AGN X-rays; 1: soft and hard; 2: hard only; 3: soft only. |
| `SpecIndexXrayAGNSoft` | `2.2` | AGN soft-band X-ray spectral index. |
| `SpecIndexXrayAGNHard` | `1.7` | AGN hard-band X-ray spectral index. |
| `SpecIndexUVAGNSoft` | `0.61` | AGN nonionizing UV spectral index, wavelengths above 912 Å. |
| `SpecIndexUVAGNHard` | `1.70` | AGN ionizing/EUV spectral index, wavelengths at or below 912 Å. |
| `AGNLWEfficiency` | `1.0` | Multiplicative normalization of the AGN Lyman–Werner amplitude. |
| `Flag_BHARExponentialCut` | `0` | Select randomized exponential accretion/emissivity timing rather than the duty-cycle-weighted source treatment. |
| `Flag_OutputXrayLF` | `0` | Write X-ray luminosity-function histograms and root emissivity histories. The current writer also requires `Flag_IncludeSpinTemp=1`, which allocates those history arrays. |
| `XrayLF_MinLogL` | `38.0` | Lower log10 X-ray luminosity bound, luminosity in erg s⁻¹. |
| `XrayLF_MaxLogL` | `46.0` | Upper log10 X-ray luminosity bound, luminosity in erg s⁻¹. |
| `XrayLF_BinsPerDex` | `5` | X-ray histogram bins per luminosity dex. |

### Star formation and Pop. III controls

Minihalo/Pop. III terms are conditional on `USE_MINI_HALOS`; see [Galaxy physics](galaxy-physics.md).

| Parameter | Default | Meaning / units |
|---|---|---|
| `SfDiskVelOpt` | `1` | 1: Vmax; 2: Vvir in the star-formation disk prescription. |
| `SfPrescription` | `1` | 1: critical-surface-density law; 2: pressure-based molecular-gas law. See Galaxy physics. |
| `SfEfficiency` | `0.08` | Star-formation efficiency normalization. |
| `SfEfficiency_III` | `0.008` | Pop. III star-formation efficiency normalization. |
| `SfEfficiencyScaling` | `0.0` | Redshift scaling of the star-formation efficiency. |
| `SfEfficiencyScaling_III` | `0.0` | Pop. III counterpart of SfEfficiencyScaling. |
| `SfCriticalSDNorm` | `0.2` | Critical surface-density normalization in the implemented internal-unit law. |
| `SfCriticalSDNorm_III` | `0.2` | Pop. III counterpart of SfCriticalSDNorm. |
| `PopIII_IMF` | `1` | 1: Sal500_001; 2: Sal500_050; 3: logA500_001; 4: logE500_001. |
| `PopIIIAgePrescription` | `2` | 1: Schaerer strong-mass-loss lifetimes; 2: no-mass-loss lifetimes. |

### Stellar feedback

| Parameter | Default | Meaning / units |
|---|---|---|
| `Flag_IRA` | `0` | Use instantaneous recycling instead of the delayed-feedback tables. |
| `Flag_ReheatToFOFGroupTemp` | `0` | Reheat using the FoF virial temperature instead of the subhalo temperature. |
| `SfRecycleFraction` | `0.25` | Instantaneous recycled mass fraction used by IRA. |
| `SfRecycleFraction_III` | `0.25` | Pop. III IRA recycled fraction. |
| `Yield` | `0.03` | IRA metal yield per unit formed stellar mass. |
| `Yield_III` | `0.03` | Pop. III IRA metal yield. |
| `SnModel` | `1` | 1: Guo-style velocity factors; 2: broken power-law velocity factors; see Galaxy physics. |
| `SnEjectionRedshiftDep` | `0.0` | SN energy-coupling redshift exponent; see the selected SnModel. |
| `SnEjectionRedshiftDep_III` | `0.0` | Pop. III counterpart of SnEjectionRedshiftDep. |
| `SnEjectionEff` | `0.5` | SN energy-coupling efficiency normalization; see the selected SnModel. |
| `SnEjectionEff_III` | `0.5` | Pop. III counterpart of SnEjectionEff. |
| `SnEjectionScaling` | `2.0` | SN energy-coupling high-velocity exponent; see the selected SnModel. |
| `SnEjectionScaling_III` | `2.0` | Pop. III counterpart of SnEjectionScaling. |
| `SnEjectionScaling2` | `2.0` | SN energy-coupling low-velocity exponent; see the selected SnModel. |
| `SnEjectionScaling2_III` | `2.0` | Pop. III counterpart of SnEjectionScaling2. |
| `SnEjectionNorm` | `70.0` | SN energy-coupling velocity pivot, km s⁻¹; see the selected SnModel. |
| `SnEjectionNorm_III` | `70.0` | Pop. III counterpart of SnEjectionNorm. |
| `SnReheatRedshiftDep` | `0.0` | SN reheated-mass/loading redshift exponent; see the selected SnModel. |
| `SnReheatRedshiftDep_III` | `0.0` | Pop. III counterpart of SnReheatRedshiftDep. |
| `SnReheatEff` | `10.0` | SN reheated-mass/loading efficiency normalization; see the selected SnModel. |
| `SnReheatEff_III` | `10.0` | Pop. III counterpart of SnReheatEff. |
| `SnReheatLimit` | `10.0` | SN reheated-mass/loading maximum mass-loading factor; see the selected SnModel. |
| `SnReheatLimit_III` | `10.0` | Pop. III counterpart of SnReheatLimit. |
| `SnReheatScaling` | `0.0` | SN reheated-mass/loading high-velocity exponent; see the selected SnModel. |
| `SnReheatScaling_III` | `0.0` | Pop. III counterpart of SnReheatScaling. |
| `SnReheatScaling2` | `0.0` | SN reheated-mass/loading low-velocity exponent; see the selected SnModel. |
| `SnReheatScaling2_III` | `0.0` | Pop. III counterpart of SnReheatScaling2. |
| `SnReheatNorm` | `70.0` | SN reheated-mass/loading velocity pivot, km s⁻¹; see the selected SnModel. |
| `SnReheatNorm_III` | `70.0` | Pop. III counterpart of SnReheatNorm. |
| `SnMetalRetentionFraction` | `0.0` | Fraction of reheated cold-gas metals retained in cold gas; constrained to [0,1]. |

### Cooling and reincorporation

| Parameter | Default | Meaning / units |
|---|---|---|
| `MaxCoolingMassFactor` | `1.0` | Maximum cooling/free-fall mass factor. |
| `ReincorporationModel` | `1` | 1: halo-dynamical-time prescription; 2: mass-dependent prescription. |
| `ReincorporationEff` | `0.0` | Model-dependent reincorporation efficiency; model 2 uses Myr normalization. |

### Mergers and infall

| Parameter | Default | Meaning / units |
|---|---|---|
| `Flag_FixVmaxOnInfall` | `0` | Preserve the infall Vmax for satellites. |
| `Flag_FixDiskRadiusOnInfall` | `0` | Preserve the infall disk radius for satellites. |
| `ThreshMajorMerger` | `0.3` | Registered legacy major-merger threshold; no production use appears in this revision. |
| `MergerTimeFactor` | `0.5` | Multiplicative dynamical-friction timescale factor. |
| `MinMergerStellarMass` | `1e-9` | Minimum stellar mass for merger-burst/friction treatment, internal mass units. |
| `MinMergerRatioForBurst` | `0.1` | Minimum merger ratio for a starburst. |
| `MergerBurstFactor` | `0.57` | Merger-burst mass-fraction normalization. |
| `MergerBurstScaling` | `0.7` | Merger-burst mass-ratio exponent. |

### Black-hole growth and feedback

| Parameter | Default | Meaning / units |
|---|---|---|
| `Flag_BHFeedback` | `1` | Enable the BH feedback prescription. |
| `RadioModeEff` | `0.3` | Radio-mode accretion efficiency parameter. |
| `QuasarModeEff` | `0.0005` | Quasar-mode feedback coupling parameter. |
| `BlackHoleGrowthRate` | `0.05` | Merger-driven BH cold-gas accretion normalization. |
| `EddingtonRatio` | `1.0` | Accretion Eddington-ratio parameter. |
| `BlackHoleSeed` | `1e-7` | BH seed mass in internal mass units. |
| `BlackHoleMassLimitReion` | `-1` | BH mass cutoff for ionizing sources; negative disables the cutoff. |
| `quasar_mode_scaling` | `0.0` | Redshift scaling of quasar-mode BH growth. |
| `quasar_open_angle` | `80.0` | Quasar opening angle, degrees. |

### Reionization, escape fraction and filtering

| Parameter | Default | Meaning / units |
|---|---|---|
| `Flag_ReionizationModifier` | `1` | 0: no infall suppression; 1: Sobacchi-style; 2: Gnedin-style; 3: precomputed critical-mass history. |
| `ReionSobacchi_Zre` | `9.3` | Global Sobacchi prescription characteristic reionization redshift. |
| `ReionSobacchi_DeltaZre` | `1.0` | Global Sobacchi reionization-history width. |
| `ReionSobacchi_DeltaZsc` | `2.0` | Global Sobacchi redshift-transition parameter. |
| `ReionSobacchi_T0` | `5.0e4` | Global Sobacchi temperature normalization, K. |
| `ReionGnedin_z0` | `8` | Gnedin prescription initial characteristic redshift. |
| `ReionGnedin_zr` | `7` | Gnedin prescription reionization characteristic redshift. |
| `Flag_PatchyReion` | `1` | Enable the spatial radiation/ionization calculation. |
| `Flag_OutputGrids` | `1` | Request spatial grid outputs; the thermal wrapper can additionally write source inputs required by its path. |
| `Flag_OutputGridsPostReion` | `1` | Continue the grid-output/calculation policy after reionization. |
| `Flag_FescCGMSuppression` | `0` | 0: off; 1: instantaneous Gamma12; 2: accumulated Gamma12; 3: clumping-factor modulation. |
| `ReionUVBFlag` | `1` | 0: decoupled; 1: store UVB at ionization; 2: update UVB after ionization. |
| `ReionGridDim` | `128` | Cells per side of the radiation grid. |
| `ReionDeltaRFactor` | `1.1` | Ratio between successive excursion-set filtering radii. |
| `ReionFilterType` | `0` | Radiation filter selector: 0 real-space top-hat; 1 sharp-k; 2 Gaussian. |
| `ReionPowerSpecDeltaK` | `0.1` | Registered legacy bin parameter; the current PS routine instead hardcodes geometric bin growth by 1.35. |
| `ReionRtoMFilterType` | `0` | Radius-to-mass volume convention: 0 top-hat, 1 Gaussian. |
| `Y_He` | `0.24` | Primordial helium mass fraction. |
| `ReionRBubbleMin` | `0.4068` | Minimum excursion-set bubble/filter radius, h⁻¹ cMpc. |
| `ReionRBubbleMax` | `20.34` | Fixed maximum bubble radius without the recombination/evolving-radius branch, h⁻¹ cMpc. |
| `ReionGammaHaloBias` | `2.0` | UVB halo-bias factor. |
| `ReionAlphaUV` | `2.0` | Stellar UV spectral index used in the UVB normalization. |
| `ReionAlphaUVBH` | `2.0` | BH UV spectral index in the relevant UVB source conversion. |
| `EscapeFracDependency` | `1` | 0: constant; 1: redshift; 2: stellar mass; 3: SFR; 4: cold-gas surface density; 5: halo mass; 6: specific SFR. |
| `EscapeFracNorm` | `0.06` | Stellar escape-fraction normalization. |
| `EscapeFracNormIII` | `0.06` | Pop. III escape-fraction normalization. |
| `EscapeFracRedshiftOffset` | `6.0` | Escape-fraction redshift pivot. |
| `EscapeFracRedshiftScaling` | `0.5` | Escape-fraction redshift exponent. |
| `EscapeFracPropScaling` | `0.5` | Galaxy-property exponent for EscapeFracDependency > 1. |
| `EscapeFracBHNorm` | `1` | BH escape-fraction normalization. |
| `EscapeFracBHScaling` | `0` | BH escape-fraction redshift exponent. |
| `EscapeFracScatterDex` | `0.0` | Scatter in log10 stellar escape fraction, dex. |
| `Flag_SourceRecalibration` | `0` | Recalibrate the modified stellar/X-ray source amplitudes against the baseline history. |
| `FescCGMSuppressionNorm` | `0.00008` | CGM suppression normalization. |
| `FescCGMSuppressionScaling` | `0.2` | CGM column-density exponent. |
| `FescCGMGamma12Scaling` | `6.0` | CGM UVB/clumping modulation exponent. |
| `ReionSMParam_m0` | `0.18984` | Sobacchi critical-mass normalization, internal mass units. |
| `ReionSMParam_a` | `0.17` | Sobacchi UVB-intensity exponent. |
| `ReionSMParam_b` | `-2.1` | Sobacchi redshift exponent. |
| `ReionSMParam_c` | `2.0` | Sobacchi ionization-history exponent. |
| `ReionSMParam_d` | `2.5` | Sobacchi ionization-history exponent. |
| `ReionTcool` | `1.0e4` | Atomic-cooling virial-temperature threshold, K. |
| `ReionNionPhotPerBary` | `4000` | Ionizing photons per stellar baryon. |
| `ReionSfrTimescale` | `0.5` | Legacy SFR-averaging timescale factor. |
| `TsHeatingFilterType` | `1` | Thermal-history filter selector: 0 real-space top-hat; 1 sharp-k; 2 Gaussian. |
| `TsNumFilterSteps` | `40` | Number of thermal-history filtering steps. |
| `TsVelocityComponent` | `3` | 1: x velocity; 2: y; 3: z. |
| `EndRedshiftLightcone` | `5.0` | Low-redshift endpoint of the requested lightcone. |
| `ReionRBubbleMaxRecomb` | `33.9` | Fixed maximum bubble radius with recombinations, h⁻¹ cMpc; replaced when the evolving-radius flag is active. |
| `ReionMaxHeatingRedshift` | `30.` | Heating-history upper-redshift boundary; must not exceed the first input snapshot redshift. |

### Photometry and dust

Magnitude-related parameters are used by `CALC_MAGS`; see [Galaxy physics](galaxy-physics.md).

| Parameter | Default | Meaning / units |
|---|---|---|
| `BirthCloudLifetime` | `10e6` | Birth-cloud stellar-age boundary, yr. |
| `DustMetallicityScale` | `1.2` | Metallicity exponent in dust optical depth. |
| `DustTauUVISM` | `13.5` | ISM UV optical-depth normalization. |
| `DustNISM` | `-1.6` | ISM wavelength attenuation exponent. |
| `DustTauUVBC` | `381.3` | Birth-cloud UV optical-depth normalization. |
| `DustNBC` | `-1.6` | Birth-cloud wavelength attenuation exponent. |
| `DustAZ` | `-0.35` | Redshift coefficient in the dust attenuation factor. |
| `TargetSnaps` | `-1` | Magnitude snapshot selection; align with MAGS_N_SNAPS and saved outputs. |
| `RestBands` | `1550,1650` | Comma-separated rest-frame top-hat wavelength boundaries, Å; the default pair specifies one band. |
| `BetaBands` | Empty | Comma-separated UV-slope band boundaries; empty by default. |
| `InstantSfIII` | `0` | 0: continuous Pop. III SF templates; 1: instantaneous burst templates. |
| `DeltaT` | `1.0` | Pop. III instantaneous-burst time within the snapshot, Myr. |

### Distribution functions

| Parameter | Default | Meaning / units |
|---|---|---|
| `Flag_OutputHMF` | `1` | Write the halo mass function. |
| `HMF_MinMass` | `8.0` | Lower log10 halo-mass bound, mass in M☉/h. |
| `HMF_MaxMass` | `15.0` | Upper log10 halo-mass bound, mass in M☉/h. |
| `HMF_BinsPerDex` | `2` | Halo-mass bins per dex. |
| `Flag_OutputSMF` | `1` | Write the stellar mass function. |
| `SMF_MinMass` | `6.0` | Lower log10 stellar-mass bound, mass in M☉. |
| `SMF_MaxMass` | `13.0` | Upper log10 stellar-mass bound, mass in M☉. |
| `SMF_BinsPerDex` | `2` | Stellar-mass bins per dex. |
| `Flag_OutputUVLF` | `1` | Write the intrinsic UV luminosity function; requires CALC_MAGS. |
| `UVLF_MinMag` | `-28.0` | Numerically lower (brighter) absolute-magnitude limit. |
| `UVLF_MaxMag` | `-8.0` | Numerically upper (fainter) absolute-magnitude limit. |
| `UVLF_BinsPerMag` | `2` | UV magnitude bins per magnitude. |
| `Flag_OutputDustyLF` | `1` | Write the dust-attenuated UV luminosity function; requires CALC_MAGS. |
| `Flag_OutputQuasarLF` | `1` | Write the quasar UV luminosity function with AGN duty-cycle weighting. |
| `Flag_OutputOIIILF` | `1` | Write the [O III] luminosity function. |
| `OIIILF_MinLogL` | `38.0` | Lower log10 [O III] luminosity bound, luminosity in erg s⁻¹. |
| `OIIILF_MaxLogL` | `45.0` | Upper log10 [O III] luminosity bound, luminosity in erg s⁻¹. |
| `OIIILF_BinsPerDex` | `2` | [O III] luminosity bins per dex. |

## Configuration relationships to check

- `NSteps` must equal 1. Increasing temporal resolution means using a finer
  input snapshot sequence, not requesting unsupported substeps.
- `USE_STOCHASTICITY=OFF` rejects nonzero escape-fraction scatter, X-ray scatter,
  no-SFR or recalibration requests. Escape-fraction scatter and no-SFR are
  mutually exclusive; recalibration requires an active source modification.
- `Flag_IncludeSpinTemp` is rejected with CUDA and with MCMC. Its upper heating
  redshift must be no higher than the first snapshot redshift.
- Power-spectrum and lightcone flags do not automatically enable brightness
  calculation. The lightcone and thermal solver are called in the coupled
  `ReionUVBFlag` branch; see [Workflow](workflow.md).
- CGM escape-fraction modulation samples recombination information in the
  patchy UVB branch; use the full feature combination documented in [IGM](igm.md).
- The parser validates `SnMetalRetentionFraction` in the range [0,1]. For
  magnitude runs, match the filter and target-snapshot counts to their
  compile-time dimensions.

Source-default values provide a reproducible starting configuration, but are
not sufficient to identify a calibrated physical model. Record both the
compiled options and the resolved parameter hierarchy when describing a model,
and cite the [feature papers](references.md) appropriate to its prescriptions.
