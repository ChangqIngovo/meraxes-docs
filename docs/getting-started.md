# Build and run

## Dependencies

| Dependency | Use |
|---|---|
| C compiler, CMake and Make | Compile Meraxes. |
| MPI | Parallel execution. |
| Parallel HDF5, including the high-level library | Read and write simulation data. |
| GSL and CBLAS | Numerical integration, interpolation and random draws. |
| FFTW single-precision and MPI libraries | Distributed radiation grids. |
| Git and bundled `mlog` | Build metadata and logging. |
| Sector | Required only for stellar photometry. |

Use HDF5 and FFTW libraries built with the same MPI implementation.

## Configure and compile

From the Meraxes source directory:

```sh
mkdir build
cd build
cmake ..
make
```

This creates `bin/meraxes` and `input.par` in the build directory.
Enable additional physics by adding the relevant option to `cmake ..`, then
run `make` again:

| Option | Capability |
|---|---|
| `-DUSE_STOCHASTICITY=ON` | Escape-fraction and X-ray scatter, no-SFR and source recalibration. |
| `-DUSE_MINI_HALOS=ON` | Molecular cooling, Pop. III stars and associated feedback. |
| `-DCALC_MAGS=ON -DSECTOR_ROOT=/path/to/sector/clib` | Stellar photometry. |
| `-DUSE_JWST=ON` / `-DUSE_HST=ON` | Observed filters for photometry builds. |
| `-DN_HISTORY_SNAPS=17` | Number of snapshots retained for delayed stellar feedback. |
| `-DMAGS_N_SNAPS=12 -DMAGS_N_BANDS=11` | Photometry array dimensions; match the selected snapshots and bands. |

The additional physics options are off by default. Stellar-feedback history
must cover the ages required by the feedback tables.

## Configure a run

Edit the generated `input.par`:

| Set | Purpose |
|---|---|
| `SimParamsFile` and `SimulationDir` | Select the simulation parameters and data. |
| Table directories | Locate cooling, stellar-feedback and enabled radiation/photometry tables. |
| `OutputDir`, `FileNameGalaxies`, `OutputSnapshots` | Choose where and when to save results. |
| Physics parameters and flags | Select the model and requested products. |

The [input reference](inputs.md) lists filenames, defaults and parameter meanings.

## Run

```sh
/path/to/meraxes /path/to/input.par
```

For cluster runs, see the [submission-file example](#submission-file).

### Submission file

On Gadi, save this minimal submission file as `submit.pbs` in the build directory:

```bash
#!/bin/bash
#PBS -P PROJECT
#PBS -l ncpus=48,mem=128GB,walltime=04:00:00
#PBS -l storage=gdata/PROJECT+scratch/PROJECT
#PBS -l wd
#PBS -V

mpirun -np "$PBS_NCPUS" ./bin/meraxes input.par
```

Replace `PROJECT`, adjust resources and include the storage projects used by
the run. Submit with the build modules loaded; `-V` inherits that environment.

```sh
qsub submit.pbs
```

See NCI's [PBS guide](https://opus.nci.org.au/spaces/Help/pages/90308829/PBS+Directives+Explained)
for scheduler options and [Post-processing tools](post-processing.md) for analysing results.
