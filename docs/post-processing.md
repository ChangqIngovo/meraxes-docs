# Post-processing tools

[DRAGONS](https://meraxes-devs.github.io/dragons/meraxes.html) provides Python readers, galaxy histories, reionization diagnostics and standard plots for Meraxes output. Start from the master HDF5 file; the readers follow its links to the rank catalogues and grids.

## Install and open a run

```sh
python -m pip install "git+https://github.com/meraxes-devs/dragons.git"
```

The package installs its Python dependencies, including NumPy, h5py, Astropy, pandas, SciPy, Matplotlib and Astrodatapy. Its grid extensions require a C compiler during installation.

```python
from dragons import meraxes
from dragons.meraxes import io

fname = "meraxes.hdf5"
io.set_little_h(fname)
params = io.read_input_params(fname)
units = io.read_units(fname)
snapshots, redshifts, lookback_times = io.read_snaplist(fname)
snapshot = int(snapshots[-1])
```

`set_little_h(fname)` uses the simulation's `Hubble_h` for subsequent reads. This removes the stored h factors; it does not change a mass expressed in units of 10¹⁰ Msun into Msun. `set_little_h()` resets the default to unscaled reads. A per-call `h=` overrides the default. Use the same convention for galaxy properties, box size and volume.

## Metadata and snapshot selection

These calls read metadata without loading galaxy catalogues or radiation cubes.

| Function in `meraxes.io` | Result and controls |
| --- | --- |
| `read_input_params(fname, h=None, raw=False)` | Parameter dictionary, including nested parameter groups. Also adds `Volume` and saved model metadata; `raw=True` omits these additions. With h scaling, rescales `BoxSize` and `PartMass`. |
| `read_units(fname)` | Unit dictionary, including grid units and the nested `HubbleConversions` dictionary. |
| `read_git_info(fname)` | Pair `(ref, diff)` stored in `gitdiff`. |
| `set_little_h(h=None)` | Set the default h value using a number or master filename; return the resulting default. `None` or `1.0` resets it. |
| `read_snaplist(fname, h=None)` | Three arrays: snapshot numbers, redshifts and lookback times. Time is in Myr after h conversion. |
| `check_for_redshift(fname, redshift, tol=0.1)` | Closest `(snapshot, redshift)` within the tolerance; raises `KeyError` when none qualifies. |
| `check_for_global_xH(fname, xH, tol=0.1)` | Closest `(snapshot, redshift, neutral_fraction)` using volume-weighted neutral fractions; raises `KeyError` outside the tolerance. |
| `grab_redshift(fname, snapshot)` | Redshift of one snapshot. Negative snapshot numbers select backwards from the saved outputs. |
| `grab_unsampled_snapshot(fname, snapshot)` | Original simulation snapshot number from `UnsampledSnapshot`, where that attribute is present. |

For comparisons at a common reionization stage, use `check_for_global_xH` rather than matching snapshot numbers between models. Snapshot numbers identify outputs; their corresponding redshifts come from `read_snaplist`.

## Galaxy catalogues

```python
gals = io.read_gals(
    fname, snapshot=snapshot,
    props=["ID", "Type", "StellarMass", "Sfr"],
)
stellar_mass = gals["StellarMass"] * 1e10  # Msun after h conversion
```

`read_gals` concatenates `Core0`, `Core1`, and subsequent rank catalogues in numerical order. It reads only the requested fields, but allocates the requested rows together in memory.

```python
io.read_gals(fname, snapshot=None, props=None, sim_props=False,
             pandas=False, table=False, h=None, indices=None)
```

| Argument | Meaning |
| --- | --- |
| `snapshot` | Snapshot number; `None` or `-1` selects the last saved snapshot. Other negative values count backwards through saved snapshots. |
| `props` | List of field names; `None` selects every field. Available names are listed in [Outputs](outputs.md). |
| `indices` | Unique row indices in the concatenated catalogue, not galaxy IDs. The reader sorts them before reading. |
| `pandas`, `table` | Choose a pandas DataFrame or an Astropy Table. The default is a NumPy structured array; choose only one alternative. |
| `sim_props` | Return `(galaxies, parameters)` instead of galaxies alone; the parameters include the snapshot redshift. |
| `h` | Apply the field-specific conversions stored in the master file. |

For a small subset, combine `props` with `indices`. For bounded memory use, read one rank at a time in blocks:

```python
import h5py

with h5py.File(fname, "r") as f:
    snap = f[f"Snap{snapshot:03d}"]
    cores = sorted((k for k in snap if k.startswith("Core")),
                   key=lambda k: int(k[4:]))
    for core in cores:
        dataset = snap[f"{core}/Galaxies"]
        fields = dataset.fields(["ID", "StellarMass", "Sfr"])
        for start in range(0, len(dataset), 250_000):
            block = fields[start:start + 250_000]
            # Analyse or write this block before the next read.
```

Direct h5py reads preserve stored units and rank-local indices. Apply the unit conversions from the master metadata to each block. The merger readers below convert non-negative indices into the concatenated catalogue's row numbering.

## Galaxy histories and merger links

The history tool follows saved galaxy links across snapshots. Supply the target's `ID`, the snapshot where it is selected, and the properties to track.

```python
history = meraxes.galaxy_history(
    fname, gal_id=target_id, snapshot=snapshot,
    props=["ID", "StellarMass", "Sfr", "ColdGas"],
)
```

Here `target_id` is a selected galaxy ID. Include `ID` in `props`, because it locates the target in the starting catalogue.

| Function | Returned data |
| --- | --- |
| `meraxes.galaxy_history(fname, gal_id, snapshot, future_snapshot=-1, pandas=False, props=None)` | Structured array of the first-progenitor history, indexed by snapshot number. Set `pandas=True` for a DataFrame. |
| `io.read_firstprogenitor_indices(fname, snapshot, pandas=False)` | For each galaxy, the first-progenitor row in the previous snapshot. |
| `io.read_nextprogenitor_indices(fname, snapshot, pandas=False)` | Next progenitor sharing the same descendant, indexed within the current snapshot. |
| `io.read_descendant_indices(fname, snapshot, pandas=False)` | Descendant row in the following snapshot. |

The index readers return NumPy arrays, or pandas Series with `pandas=True`; `-1` means no link. They require the corresponding datasets and adjacent snapshots. The history reader follows consecutive snapshot numbers, so the relevant catalogues must be saved. Unvisited history rows remain zero-filled. A target with no first progenitor raises `Warning`.

Set `future_snapshot` beyond the starting snapshot to follow descendants as well. The result becomes `(history, merged_snapshot)`; `merged_snapshot` records when the tracked galaxy becomes a non-primary progenitor, or remains `-1` if no such merger is recorded along the inspected links.

## Grids and global histories

Use stored global statistics for redshift evolution and load cubes only for spatial analyses.

```python
xh_volume = io.read_global_xH(fname, snapshots, weight="volume")
xh_mass = io.read_global_xH(fname, snapshots, weight="mass")
```

| Function in `meraxes.io` | Result and controls |
| --- | --- |
| `list_grids(spec, fname, snapshot)` | Names of three-dimensional datasets. `spec=0` selects `Grids`; `spec=1` selects `MetalGrids`. |
| `read_grid(spec, fname, snapshot, name, h=None, h_scaling={})` | Entire cube as a NumPy array, reshaped using `ReionGridDim` or `MetalGridDim`. The same `spec` convention applies. |
| `read_global_xH(fname, snapshot, weight="volume")` | Stored volume- or mass-weighted neutral fraction. Accepts one snapshot or a sequence; returns a scalar or array. Missing values are `NaN`. |
| `read_global_J_21(fname, snapshot)` | Volume-averaged UV intensity, as a scalar or array. Reads saved attributes where available; otherwise loads and averages the `J_21` cubes. |
| `read_ps(fname, snapshot)` | Tuple `(k, power, error)` from `k_bins`, `PS_data` and `PS_error`. This reads an existing spectrum. |

`read_grid` uses the saved `HubbleConversions/Grids` entries when h scaling is requested. Its `h_scaling` argument is not applied by the implementation. Before reading metal cubes, call `io.set_little_h()` to restore unscaled reads and use their `Units/MetalGrids` metadata; they have no separate h-conversion registry.

For a plane, subvolume, lightcone, or an attribute-only dataset, use h5py directly:

```python
import h5py

with h5py.File(fname, "r") as f:
    grids = f[f"Snap{snapshot:03d}/Grids"]
    for name, dataset in grids.items():
        print(name, dataset.shape, dict(dataset.attrs))
    xh = grids["xH"]
    if xh.ndim == 3:
        plane = xh[0, :, :]
```

`list_grids` omits one-dimensional spectra and empty datasets holding summary attributes. `read_grid` assumes a cubic volume and cannot read these products or a rectangular lightcone. `read_ps` expects its three named datasets; use the dataset names in [Outputs](outputs.md) when a file stores additional or differently named spectra. The power values are returned without a unit conversion or re-normalization.

## Reionization diagnostics

`meraxes.electron_optical_depth(fname, volume_weighted=False)` returns `(redshifts, optical_depth)`, integrated from redshift zero to each saved redshift. The default uses the mass-weighted ionized fraction. The calculation assumes completed hydrogen reionization below the final saved redshift and doubly ionized helium below redshift four. `volume_weighted=True` substitutes a volume-weighted history for comparison.

The helper calls SciPy's former `integrate.simps` API. With SciPy 1.14 or newer, update that call to `integrate.simpson(values, x=redshifts)` before using it; see the [SciPy API change](https://docs.scipy.org/doc/scipy/release/1.14.0-notes.html#expired-deprecations).

## Standard plots

`MeraxesOutput` connects the catalogue readers to Matplotlib and observational compilations from Astrodatapy. Its constructor sets the reader's default h to the run's value. Individual methods return `(figure, axes)` and optionally save a PDF.

```python
from dragons.meraxes.plots import MeraxesOutput

run = MeraxesOutput(fname, plot_dir="plots", save=True)
fig, ax = run.plot_smf(redshift=float(redshifts[-1]))
```

For methods accepting `gals`, pass an already h-corrected catalogue with the required fields. Otherwise the method reads those fields itself. `imfscaling` converts the Salpeter-based observational mass or SFR scale to the chosen IMF; its default is `1.0`.

| Method | Required product and plotted quantity |
| --- | --- |
| `plot_smf(redshift, imfscaling=1.0, gals=None)` | `StellarMass`: stellar mass function and observational comparison. |
| `plot_sfrf(redshift, imfscaling=1.0, gals=None)` | `Sfr`: star-formation-rate function and observational comparison. |
| `plot_uvlf(redshift, mag_index=None, gals=None)` | `DustyMags`: UV luminosity function. Select the UV band with `mag_index`; the default selects the last column. |
| `plot_HImf(redshift, gals=None)` | `HIMass`: atomic-hydrogen mass function. |
| `plot_bhmf(redshift, gals=None)` | `BlackHoleMass`: black-hole mass function. |
| `plot_bolometric_qlf(redshift, gals=None)` | Black-hole mass, accreted hot/cold masses and `dt`: bolometric quasar luminosity function. This routine is marked unfinished in the implementation. |
| `plot_sfr_evo(sfr_evo=None)` | Cosmic SFR density. An optional array supplies the total SFR in each saved snapshot; the routine divides by the simulation volume. |
| `plot_xHI()` | Stored global neutral fractions: reionization history. |
| `plot_21cmPS()` | Saved power spectra at multiple redshifts. |

The UV, neutral-fraction and power-spectrum methods can return an empty list when the required output is absent. The neutral-fraction plot extends the history to fully neutral/ionized endpoints; use `read_global_xH` for the unmodified saved values. Choose individual plot methods for runs that save only selected products.

`allplots(meraxes_fname, output_dir, uvindex=None, save=False, imfscaling=1.0)` calls the standard suite and returns a list of plotting results. It attempts available redshifts from 8 to 0, followed by the SFR, neutral-fraction and power-spectrum histories. The equivalent command-line entry point is:

```sh
python -m dragons.meraxes.plots meraxes.hdf5 --output_dir plots
```

Its options are `--output_dir` (or `-o`), `--uvindex`, and `--imfscaling`. The command saves the plots. Use `--uvindex` to match the photometry band ordering of the run.

## Derived black-hole observables

`meraxes.bh_bolometric_mags(gals, simprops, eta=0.06, quasarVoLScaling=0.0, seed=None, consider_opening_angle=False)` estimates one bolometric magnitude per galaxy from its accretion history.

| Input or option | Use |
| --- | --- |
| `gals` | H-corrected `BlackHoleMass`, `BlackHoleAccretedHotMass`, `BlackHoleAccretedColdMass`, and `dt`. Masses retain the catalogue's 10¹⁰ Msun unit; time is in Myr. |
| `simprops` | Parameter dictionary from `read_input_params`, containing `EddingtonRatio` and `quasar_open_angle`. |
| `eta` | Radiative efficiency, default `0.06`. |
| `seed` | NumPy random seed; use a positive integer for a repeatable draw. |
| `consider_opening_angle` | Randomly select observable orientations using the quasar opening angle. |
| `quasarVoLScaling` | Add a black-hole-mass dependence to the observable opening fraction; positive values also enable orientation selection. |

The helper samples an observation time within the snapshot and weights the luminosity by the quasar accretion duty cycle. Unobserved or zero-luminosity objects have non-finite magnitudes; select finite values before binning. Its duty-cycle treatment also weights the radio contribution with the quasar-mode accretion time.

`meraxes.bh_radio_lum(gals)` is an unfinished radio-luminosity helper and currently reaches an invalid `np.log10()` call. It has no usable return value without correcting the implementation.

## Common analysis utilities

`dragons.munge` supplies the binning and grid operations used by the plotting tools.

| Function | Result and usage |
| --- | --- |
| `mass_function(mass, volume, bins, range=None, poisson_uncert=False, return_edges=False, **kwargs)` | Binned number density per unit of the supplied coordinate. Return columns are bin centre and density, with an optional Poisson uncertainty. `return_edges=True` also returns bin edges. Use evenly spaced bins; supply log masses for a density per dex. |
| `edges_to_centers(edges, width=False)` | Centres of evenly spaced bins; also returns their width when requested. |
| `ndarray_to_dataframe(arr, drop_vectors=False)` | Structured array to DataFrame; one-dimensional vector fields become columns such as `Pos_0`. `drop_vectors=True` keeps scalar fields only. |
| `pretty_print_dict(d, fmtlen=30)` | Print a nested dictionary in aligned columns. |
| `describe(arr, **kwargs)` | Print and return basic distribution statistics from SciPy. |
| `smooth_grid(grid, side_length, radius, filt="tophat")` | Periodic FFT smoothing of a cube with a spherical top-hat window. Box side and smoothing radius use the same length unit. |
| `power_spectrum(grid, side_length, n_bins, dimensional=False)` | FFT power estimate returning mean wavenumber, power per logarithmic interval and a mode-count uncertainty. `dimensional=True` also returns dimensional power and its uncertainty. |

For example, build a stellar mass function from the selected catalogue:

```python
import numpy as np
from dragons import munge

positive = stellar_mass > 0
smf = munge.mass_function(
    np.log10(stellar_mass[positive]), params["Volume"],
    bins=np.arange(6.0, 12.25, 0.25), poisson_uncert=True,
)
# Columns: log10 stellar mass, number density per dex, Poisson uncertainty.
```

The grid utilities load their input arrays and FFT workspaces into memory. Their power estimator is separate from the spectra saved during a Meraxes run; its mode binning and error estimate need not reproduce the run-time estimator. Grid length units determine the reciprocal units of the returned wavenumbers, while the field units determine the power units.

API references: [Meraxes readers and diagnostics](https://meraxes-devs.github.io/dragons/meraxes.html), [analysis utilities](https://meraxes-devs.github.io/dragons/munge.html), and [plotting implementation](https://github.com/meraxes-devs/dragons/blob/master/dragons/meraxes/plots.py).
