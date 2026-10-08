# Getting started

Meraxes evolves galaxies along dark-matter halo merger trees and, when enabled,
couples their radiation sources to spatially resolved IGM calculations. A build
provides the executable; a run additionally requires compatible trees, snapshot
times, physical tables and, for the radiation calculation, simulation grids.
Start with [Inputs and configuration](inputs.md), then follow the
[execution workflow](workflow.md).

This guide describes the `forests` source at commit
[`90d8474cf41dcea646189fb86a65b7e18755ed95`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95).
The model's original formulation is [Mutch et al. (2016)](https://doi.org/10.1093/mnras/stw1506);
the [reference list](references.md) identifies subsequent feature papers.

## Build dependencies

The requirements below come from the pinned
[CMake configuration](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/CMakeLists.txt)
and [FFTW finder](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/cmake/FindFFTW.cmake).
Except for CMake and the language standard, the build does not enforce numeric
minimum library versions.

| Dependency | Requirement |
|---|---|
| CMake | Version 3.18 or later. |
| C compiler | C99 support; a CMake-compatible build backend such as Make or Ninja. |
| Git | Required for source-version metadata and the `mlog` submodule. |
| MPI | C implementation and development headers; use its matching runtime launcher. |
| HDF5 | C and high-level libraries built **with parallel support**. A serial HDF5 installation is rejected. |
| GSL | GSL and its CBLAS library. |
| FFTW | `fftw3.h`, single-precision `fftw3f` and single-precision MPI `fftw3f_mpi`. Double-precision FFTW alone is insufficient. |
| `mlog` | Bundled source submodule at `src/mlog`. |

Build MPI, HDF5 and FFTW against a consistent MPI implementation. Point CMake to
nonstandard installations through its usual discovery variables or a repository
root `local.cmake`; this file is loaded before `project()` so it can also select
the compiler. `FFTW_ROOT` can guide FFTW discovery. Package-manager and cluster
module names depend on the installation and are not part of the Meraxes API.

| Optional dependency | Feature |
|---|---|
| [Sector](https://github.com/meraxes-devs/sector) source and `objcopy` | `CALC_MAGS=ON`; set `SECTOR_ROOT` to Sector's `sector/clib` directory containing its C sources. Sector is not a listed submodule in this source snapshot. |
| Criterion | Unit tests enabled with `BUILD_TESTS=ON`. No minimum version is enforced. |
| CUDA toolkit and suitable compiler/device | Experimental `USE_CUDA=ON` build; the configured architecture is 60 and CUDA/C++ standard is 11. |
| gperftools profiler library | The profiling option searches for it through `GPERF_ROOT`; see the caveat below. |

## Configure and compile

These commands use an out-of-source build and the pinned revision. Run them in
the checkout after cloning.

```sh
git clone --branch forests --recurse-submodules https://github.com/qyx268/meraxes-devs.git
cd meraxes-devs
git checkout 90d8474cf41dcea646189fb86a65b7e18755ed95
git submodule update --init --recursive
cmake -S . -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build --parallel
```

The executable is `build/bin/meraxes`. Static-library builds also generate
`build/input.par`, replacing the source template's `@INPUT_FILE_DIR@` tokens
with the checkout's input-table paths. Use this generated file as a starting
point; the unconfigured `input/params/input.par` is not directly runnable.
The supplied simulation templates describe particular simulations, and their
data paths must be adapted to an available dataset.

To enable stochastic source prescriptions, configure a separate build or
reconfigure with `-DUSE_STOCHASTICITY=ON` before requesting their runtime
parameters. See [Stochasticity](stochasticity.md).

### Complete project build-option reference

These are the project-defined options and cache settings, with their **CMake
defaults**. Runtime parameters are listed separately in [Inputs](inputs.md).

| Setting | Default | Role or requirement |
|---|---|---|
| `N_HISTORY_SNAPS` | `17` | Number of snapshots retained for delayed stellar feedback. Initialization checks whether it spans the required table ages. |
| `BUILD_SHARED_LIBS` | `OFF` | Build the shared Meraxes library for external integration such as Mhysa. The executable is also built; the `setuprun` target and generated `input.par` are provided only for static builds. |
| `CALC_MAGS` | `OFF` | Compute stellar magnitudes with Sector and photometric tables. |
| `MAGS_N_SNAPS` | `12` | Compile-time number of magnitude snapshots. |
| `MAGS_N_BANDS` | `11` | Compile-time number of magnitude bands; must agree with the chosen filter setup. |
| `USE_JWST` | `OFF` | Include eight NIRCam wide bands in a magnitude build. |
| `USE_HST` | `OFF` | Include the two HST IR bands in a magnitude build. |
| `USE_MINI_HALOS` | `OFF` | Compile molecular-cooling minihalos, Pop. III stars and associated feedback/enrichment. |
| `USE_STOCHASTICITY` | `OFF` | Compile scatter, no-SFR and source-recalibration prescriptions. |
| `SECTOR_ROOT` | `<checkout>/src/sector` | Sector source directory used by `CALC_MAGS`. |
| `BUILD_TESTS` | `OFF` | Configure Criterion tests and standalone cooling/BH drivers. |
| `GDB` | `OFF` | Enable debugger handoff at `mpi_debug_here()` calls. |
| `ENABLE_PROFILING` | `OFF` | Add `-pg` and search for a profiler library. |
| `USE_CUDA` | `OFF` | Compile the GPU reionization path. |
| `CMAKE_BUILD_TYPE` | `RelWithDebInfo` | Default for single-configuration generators; alternatives include `Debug`, `Release` and `MinSizeRel`. |
| `CMAKE_INSTALL_PREFIX` | `<checkout>/target` | Default destination for installation. |

For example:

```sh
cmake -S . -B build -DUSE_STOCHASTICITY=ON -DN_HISTORY_SNAPS=25
cmake --build build --parallel
```

`Debug` defines `DEBUG` and enables additional compiler diagnostics. The source
has a separate sanitizer-selection conditional, so do not assume every Debug
configuration automatically supplies a working sanitizer setup. `Release`
adds `-march=native -ffast-math`; choose the build type deliberately when moving
binaries between CPU architectures or comparing numerical behavior.

The CUDA source glob and profiler linkage need verification before relying on
those optional paths: CUDA searches `core/*.cu`, whereas the source files reside
under `src/core/`, and the located profiler library is not subsequently linked.
The runtime explicitly rejects spin-temperature calculations in CUDA builds.
`USE_JWST` and `USE_HST` should be used with `CALC_MAGS`, although CMake does not
enforce that relationship.

## Prepare and run

```sh
cp build/input.par run.par
```

Edit `run.par` and its simulation parameter file to set the real simulation
directory, tree format, units and cosmology. Verify the table paths, snapshot
selection and enabled grid requirements using [Inputs](inputs.md). The final
requested output snapshot must exceed 1 because stellar-feedback initialization
checks its history. Pre-create parent directories if `OutputDir` is nested; the
executable creates only its immediate output directory.

The command-line interface accepts exactly one parameter-file argument:

```text
meraxes <parameterfile>
```

Launch with the MPI runtime matching the build:

```sh
mpiexec -n 4 ./build/bin/meraxes run.par
```

Use `-n 1` for a single-rank run. There are no dedicated `--help` or `--version`
options in `main()`; startup prints the embedded Git revision. Parameters are
read on rank 0 and broadcast to all ranks. See [Workflow](workflow.md) for
forest distribution, grid slabs and output assembly.

For a separate run directory, a static build offers:

```sh
RUNDIR=/path/to/run cmake --build build --target setuprun
```

This copies the executable and generated parameter file, preserving an existing
parameter file. Table and simulation data remain at their configured paths.
To install the library and executable, use `cmake --install build`; component
targets `install.lib` and `install.meraxes` are also available.

## Run the source tests

Install Criterion, then configure and build the test targets:

```sh
cmake -S . -B build-tests -DBUILD_TESTS=ON
cmake --build build-tests --parallel
ctest --test-dir build-tests --output-on-failure
```

The registered Criterion tests cover snapshot-list parsing, cooling, black-hole
feedback and emission lines. If Criterion is absent, configuration warns and
no Criterion tests are registered; a CTest report saying “No tests were found”
does not validate the model. Standalone `main_cooling` and
`main_blackhole_feedback` drivers are still built. These tests exercise selected
routines rather than validating a complete simulation or its scientific
calibration.

Source: [test targets](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/tests/CMakeLists.txt),
[entry point](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/meraxes.c)
and [parameter checks](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_params.c).
