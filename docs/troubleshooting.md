# Troubleshooting and numerical checks

Use the first failing stage to narrow a problem: build discovery, parameter parsing, table initialization, tree/grid reading, galaxy evolution, IGM calculation, or output assembly. The checks below follow the `forests` implementation at commit `90d8474cf41dcea646189fb86a65b7e18755ed95`. [Getting started](getting-started.md), [inputs](inputs.md), [workflow](workflow.md) and [outputs](outputs.md) provide the corresponding interfaces.

## Build and executable

| Symptom | Source requirement | Check or correction |
|---|---|---|
| `Meraxes requires HDF5 with parallel support` | CMake requires parallel HDF5 C and high-level libraries | Select an HDF5 installation built against the same MPI implementation as Meraxes; a serial HDF5 installation does not satisfy the build. |
| FFTW detection or `fftwf_*`/`fftwf_mpi_*` link failure | The solver uses single-precision FFTW and its MPI library | Confirm `fftw3f` and `fftw3f_mpi`, not only double-precision FFTW, are installed and discoverable. |
| Missing `src/mlog/mlog.c` | `mlog` is a source submodule | Run `git submodule update --init --recursive` in the code checkout. |
| Sector or photometric build fails | `CALC_MAGS` needs an available Sector source tree | Set `SECTOR_ROOT` to that tree and align the chosen filter tables and magnitude dimensions. |
| Scatter request aborts although the parameters exist | Stochasticity is a compile-time feature | Configure with `-DUSE_STOCHASTICITY=ON`, rebuild, then use the [stochasticity settings](stochasticity.md). |
| Executable fails after moving to a different machine | The binary uses MPI/library linkage and the selected compiler flags | Compare the build/runtime MPI implementations and dynamic-library resolution. `Release` adds `-march=native`, so its CPU instructions may depend on the build host. |

Useful build records are `build/CMakeCache.txt`, `build/compile_commands.json`, the configuration log and the startup Git revision. A CMake cache preserves the previously selected libraries; changing the environment alone may not change that selection. Inspect its HDF5, FFTW, MPI and compiler entries before reconfiguring.

```sh
git rev-parse HEAD
git submodule status
cmake -LAH -N build
```

`main()` accepts exactly one parameter-file argument. It has no independent `--help` or `--version` command. Use the MPI launcher matching the build; the required launch form is described in [Getting started](getting-started.md).

Source: [`CMakeLists.txt`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/CMakeLists.txt), [`FindFFTW.cmake`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/cmake/FindFFTW.cmake), [`meraxes.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/meraxes.c).

## Parameters and enforced combinations

| Diagnostic or behavior | Meaning | Action |
|---|---|---|
| `only works if NSteps = 1` | This revision rejects other values at startup | Set `NSteps : 1`; a larger number is not an available integration-refinement control. |
| `<WARNING> ... unrecognised parameter` followed by exit | Unknown names are fatal despite the message label | Compare the case-sensitive spelling with the [registered parameter list](inputs.md). |
| Changing a default has no effect | First assignment wins: run file, then simulation file, then defaults | Check all three files and duplicates within each file. The first occurrence also wins within one file. |
| File paths contain `@INPUT_FILE_DIR@` | The unconfigured input template was used | Start from CMake's generated `build/input.par` or replace its tokens with actual paths. |
| Relative input path cannot be opened | Paths resolve from the process working directory | Check the launch directory and use the intended path relative to it. |
| Escape-fraction scatter and no-SFR request abort | `EscapeFracScatterDex > ABS_TOL` and `Flag_RemoveSFRScatter != 0` are mutually exclusive | Select the intended stellar-source treatment. |
| Recalibration request abort | No scatter/no-SFR treatment was enabled | Pair recalibration with the source treatment it is intended to normalize. |
| X-ray scatter plus no-SFR prints a warning | The combination is allowed | Verify that both modifications are scientifically intended; the warning does not imply an abort. |
| `SnMetalRetentionFraction must be between 0 and 1` | The physical fraction is out of bounds | Use a value in $[0,1]$. |
| Spin-temperature request aborts in a CUDA build | The runtime explicitly rejects this combination | Use the CPU solver for thermal/spin-temperature calculations. |
| Spin-temperature request aborts with MCMC | The standalone source disallows that history/storage combination | Use an ordinary run for this path; the MCMC integration is not a drop-in execution mode for it. |

PS and lightcone flags do **not** automatically switch on brightness calculation. Set `Flag_Compute21cmBrightTemp=1` when requesting products derived from the brightness field. The thermal calculation also requires its coupled execution path and source histories; inspect the [workflow](workflow.md) if a flag is set but its routine never appears in the log.

`FlagInteractive` and `FlagMCMC` alter execution and storage. In particular, the standalone entry point does not call `dracarys()` for `FlagMCMC=1` with `FlagInteractive=0`; an exit without a production snapshot loop can therefore be the requested mode rather than a model failure.

Source: [`read_params.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_params.c), [`parse_paramfile.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/parse_paramfile.c), [`dracarys.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/dracarys.c).

## Snapshot timeline and physical tables

`a_list.txt` must contain expansion factors in snapshot order, not redshifts. The derived redshifts decrease through ordinary forward evolution. Every selected output index must refer to that sequence; ranges use an exclusive upper endpoint. The current slice parser does not apply a third-field stride consistently, so use explicit indices or two-endpoint ranges.

| Initialization failure | Reason and correction |
|---|---|
| `Choose larger output snapshots` | Stellar-feedback history initialization requires the final selected output snapshot to exceed 1. |
| `N_HISTORY_SNAPS is expected to be ...` | The compiled stellar-history buffer does not cover the tabulated delayed feedback for the simulation cadence. Increase `N_HISTORY_SNAPS` through CMake and rebuild; changing a runtime parameter is insufficient. |
| `ReionMaxHeatingRedshift > redshift of first snapshot ...` | The heating transition precedes the available initial history. Use a transition no higher than the first snapshot's redshift. |
| Cooling or stellar-table dataset cannot be read | Directory and dataset layout must match the table reader | Inspect the files listed in [Inputs](inputs.md), including `SD93.hdf5` and `stellar_feedback_tables.hdf5`. |
| `recfast_LCDM.dat`, collision table, stellar spectrum or deposition-table open failure | Thermal initialization cannot load a required table from `TablesForXHeatingDir` | Check the exact filename and table directory expected by `XRayHeatingFunctions.c`. |
| Recombination tables are recomputed at initialization | All matching cache files were not loaded | This is an implemented fallback. A writable `RecombinationDir` allows the generated tables to be retained for later runs. |

Magnitude builds additionally require `TargetSnaps`, band definitions, `MAGS_N_SNAPS`, `MAGS_N_BANDS` and photometric tables to agree. The magnitude configuration describes compiled array sizes as well as physical filters.

Source: [`init.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/init.c), [`stellar_feedback.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/stellar_feedback.c), [`XRayHeatingFunctions.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/XRayHeatingFunctions.c), [`recombinations.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/recombinations.c).

## Tree, forest and grid readers

Changing `TreesID` selects a different tree/grid reader; it does not convert files between formats. `0` selects VELOCIraptor, `1` gbpTrees, and `2` augmented VELOCIraptor. Match `SimulationDir`, `CatalogFilePrefix`, forest statistics, cosmology and units to one consistent dataset. The complete required layouts are in [Inputs](inputs.md).

| Failure or inconsistent input | Specific check |
|---|---|
| Forest statistics cannot be opened | VELOCIraptor modes need `meraxes_augmented_stats.h5` in the selected tree directory; gbpTrees needs `trees/forests_info.hdf5`. These files provide forest counts and allocation limits. |
| Host-index assertion in VELOCIraptor reading | Hosts must be present and precede their subhalos in the expected ordering. Check catalogue/tree consistency. |
| `Failed to identify recognised grid filetype` | The reader probes the SWIFT/postprocessed layouts listed in [Inputs](inputs.md); check those filenames, not an arbitrary density HDF5 file. |
| `n_cell ... is not divisble by ReionGridDim` | The input grid dimension must be an integer multiple of the requested radiation dimension. |
| `Grid has a resolution less than that required` | The reader downsamples; it does not reconstruct unresolved higher-resolution density. Use a supported output dimension no larger than the input. |
| Cubic-grid assertion | The three grid dimensions must match the reader's cubic-box assumptions. |
| `Not a valid velocity direction` | `TsVelocityComponent` must be 1, 2 or 3. |
| Lightcone velocity-direction abort | The VELOCIraptor grid reader requires component 3 for a lightcone along the third axis. |
| `Reio Grid / Metal Grid not an int` | In the minihalo metal path, `ReionGridDim` must be divisible by `MetalGridDim`; the metal grid cannot be finer. |

MPI ranks receive complete forests, whereas FFTW distributes radiation slabs. These two loads differ: increasing rank count does not split a single forest's galaxy evolution among ranks. Inspect the per-rank allocation and source-gridding stages when the load is uneven. Forest selection through `ForestIDFile` is explicitly marked as insufficiently tested in the pinned source; IDs must match the statistics file's sorted forest list.

The input grid is a density field. The reader converts it to overdensity. Supplying an already normalized contrast as raw `Density` changes the result. Similarly, velocity conversion depends on tree format and occurs in the brightness routine; confirm the grid producer's units before enabling a velocity correction.

Source: [`read_halos.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos.c), [`read_halos-velociraptor.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos-velociraptor.c), [`read_grids.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids.c), [`read_grids-velociraptor.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids-velociraptor.c).

## Memory and an interrupted run

A single unpadded float32 cube contains $4D^3$ bytes over the full MPI decomposition. The solver also holds padded real arrays, Fourier arrays, source histories, smoothed radiation shells, persistent IGM state and galaxy/halo storage. Thermal memory therefore grows with both the grid volume and retained history/shell count; the stored output size is not the simulation memory requirement. Interactive/MCMC modes preload halo snapshots and can change the memory scaling substantially.

The snapshot loop reports memory after important stages through `log_memory_usage()`. Compare successive stages and snapshots with the job/runtime report to locate the growth. A process killed by an external resource limit can stop before Meraxes writes an error. Preserve the complete standard output, standard error and job termination status; an absent Meraxes traceback does not establish a successful run.

An HDF5 `H5Dwrite` traceback identifies the failed write operation, not a unique cause. Read the complete lower-level HDF5/MPI stack, the target file's state and the runtime termination record together. The parallel grid file uses collective I/O, so all ranks' progress matters. A later close failure may accompany an earlier write failure.

The rank catalogues are opened with truncation for an ordinary run and remain open until the loop completes. The standard entry point does not expose a restart/checkpoint command. Before launching again into the same output directory, decide whether the incomplete files must be retained; a new run can overwrite them.

Source: [`dracarys.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/dracarys.c), [`save.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/save.c), [`reionization.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c).

## Output and metadata checks

The master file is created by rank 0 **after** the snapshot loop, rank-file closure and MPI synchronization. Its absence during a running simulation is expected. Its absence after an interrupted run does not mean no rank/grid data were written.

| Apparent output problem | Interpretation/check |
|---|---|
| Master exists but a group cannot be opened | It may be an external link whose target is missing or was moved/renamed. Copy the master, all rank catalogues and the grid files together, retaining relative filenames. |
| A grid dataset has shape `(0,)` but useful attributes | Attribute-only output creates placeholder datasets. Check shape before attempting to read a cube. |
| Spin temperature has no matching unit key | The dataset is `TS_box`, while master metadata uses `Ts_box`; these names are case-sensitive. Apply the documented K/no-$h$ conversion. |
| `residual_xH` exceeds the usual fractional range | It is stored in units of $10^{-4}$ in this revision; multiply by $10^{-4}$ before treating it as a physical residual fraction. |
| `stars` appears to disagree with catalogue `StellarMass` | `stars` contains cell sums of cumulative escaped-source mass, not surviving stellar mass. Account for escape weighting, cumulative formation and enabled treatments. |
| No grid or optional dataset at a selected snapshot | Check its physics flag, `Flag_OutputGrids`, post-reionization policy and the actual write condition in [Outputs](outputs.md). |
| `k_bins` does not match expected edges | It stores mean sampled wavenumbers; the internal PS bins use a fixed factor 1.35. |

Inspect structure before loading large arrays:

```sh
h5dump -H meraxes.hdf5
h5ls -r meraxes.hdf5
```

The actual basename follows `FileNameGalaxies`. HDF5 tools may require the external-link targets to inspect linked datasets. Python inspection and block/slice examples are in [Outputs](outputs.md).

## Scientific and numerical diagnostics

Check the quantity defined by the implementation before comparing two calculations. The following checks address concrete prescription choices and numerical boundaries.

| Quantity or comparison | Diagnostic |
|---|---|
| Stellar source strength | Compare escaped cumulative mass and escaped instantaneous rate separately. A scatter treatment changes their distributions; recalibration should be checked against its target, not against unweighted surviving stellar mass. |
| Mean radiation versus morphology | Compare ionization fields at both matched redshift and matched mean neutral fraction. Timing changes and topology changes are different measurements. |
| Neutral/electron fractions | Distinguish `xH`, thermal `x_e_box` and the subgrid residual neutral fraction. They are different stages/definitions, not three interchangeable measures of the same ionization state. |
| UV recombinations | Check whether the barrier includes sinks and whether `Flag_TemperatureDependentRec` selects the evolved temperature. The thermal fixed clumping factor 2 is separate from the UV subgrid clumping array. |
| Recombination boundary values | A very weak UVB or a temperature below the interpolation table returns zero sink rate, residual fraction one after unit conversion, and clumping factor one. Inspect these limits before interpreting abrupt cell differences. |
| UVB feedback response | Compare `z_at_ionization`, the stored/updated UV intensity and `Mvir_crit` before the next galaxy infall step; feedback uses the prior available history. |
| Thermal convergence | Refine the available snapshot cadence and radiation-shell resolution. The temperature/electron advance is one forward-Euler snapshot step, while source propagation uses separate shell quadrature. |
| Cosmology change | The thermal helpers use a matter-plus-$\Lambda$ time derivative, a separate Hubble rate including radiation, and restricted growth fits. An unsupported growth case returns `-1`; `wLambda` is not a general dark-energy evolution control. |
| Very cold/hot thermal cells | Temperatures below 0.1 K are replaced by the CMB temperature; derivative updates stop when the pre-step temperature reaches $5\times10^4$ K. Count affected cells when they influence a statistic. |
| Velocity treatment | The current brightness velocity branch requires spin-temperature evolution. Its RSD redistribution runs along the third axis; a nonzero velocity flag in saturated-temperature mode does not activate it. |
| Power near the zero global signal | The code evaluates `(T / mean - 1) * mean`; exactly zero mean gives an undefined division. Inspect `PS_data` and finite values near the absorption/emission transition. |
| PS uncertainty | `PS_error = PS_data / sqrt(N_bin)` counts stored Fourier entries; it is not thermal/instrumental noise or a full non-Gaussian covariance. |
| Lightcone resolution | Interpolation is linear in time between adjacent coeval cubes. Large snapshot intervals cannot recover unresolved temporal changes. A lightcone longer than the box repeats periodic structures. |
| Optical depth | `mass_weighted_global_tau_e` includes a fixed, fully ionized low-redshift contribution. Separate that assumption from the accumulated simulated component. |
| CPU versus CUDA | The older CUDA ionization implementation omits several CPU extensions. Use a common implemented feature set before making a numerical equivalence comparison. |
| Stochastic reproducibility | Record `RandomSeed`, source revision, MPI rank count and build flags. Random draws use a rank-local generator and depend on the sequence of galaxies processed; changing distribution can change a realization. |

The equations and the relevant source boundaries are in [IGM](igm.md), [galaxy physics](galaxy-physics.md), [black holes](black-holes.md) and [stochasticity](stochasticity.md). A convergence study should vary the input halo resolution, box volume, grid dimension, temporal cadence and relevant radiation controls separately. A baseline calibrated for one source population/grid prescription does not automatically remain calibrated after those changes.

## Tests and a useful issue report

`BUILD_TESTS=ON` registers Criterion tests only when Criterion is found. A CTest result with no tests registered is not a passing model test. The source tests cover selected routines; they do not establish whole-simulation convergence. See [Getting started](getting-started.md) for the commands.

For a reproducible issue, include the pinned source revision, CMake build options, effective parameter files, MPI rank count, tree/grid format, first failing snapshot/stage, and complete error text. If the problem concerns an output, include its dataset shape/type, attributes and link target. If it concerns a scientific statistic, state the source, ionization, thermal and velocity definitions used and the conversion to physical units.
