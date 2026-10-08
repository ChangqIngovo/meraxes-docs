# Meraxes overview

Meraxes couples semi-analytic galaxy evolution to spatially varying
reionization and thermal calculations.

## Execution flow

| Stage | Main routines | Purpose |
|---|---|---|
| Launch and initialize | `main()`, `read_parameter_file()`, `init_meraxes()`, `init_storage()` | Initialize MPI; read parameters and tables; allocate storage. |
| Load a snapshot | `dracarys()`, `read_halos()` | Read halos and update galaxy hosts. |
| Evolve galaxies | `evolve_galaxies()` | Evolve gas, stars and black holes through the enabled galaxy physics. |
| Prepare grids | `construct_baryon_grids()`, `read_grid()` | Deposit galaxy sources on the grid and read the simulation density. |
| Calculate IGM fields | `ComputeTs()`, `find_HII_bubbles()` | Calculate enabled thermal fields and ionization. |
| Calculate 21-cm products | `ComputeBrightnessTemperatureBox()`, `Compute_PS()`, `ConstructLightcone()` | Calculate enabled brightness, power-spectrum and lightcone products. |
| Save outputs | `write_snapshot()`, grid writers | Write selected galaxy and grid products. |
| Assemble the master | `create_master_file()` | Rank 0 creates `meraxes.hdf5` after the snapshot loop. |

## Output structure

`Snap` below denotes a snapshot group. Its on-disk name includes the snapshot
number. The number of `Core` groups follows the MPI rank count.

| Location | Contents |
|---|---|
| `meraxes.hdf5` | Master metadata and snapshot groups. |
| `Snap` | Snapshot attributes and links to saved products. |
| `Snap/Core<rank>` | Rank-specific galaxy catalogues and progenitor indices. |
| `Snap/Grids` | Link to the snapshot's grid file. |

## Read metadata

```python
import h5py

with h5py.File("meraxes.hdf5", "r") as f:
    snapshot_names = sorted(name for name in f if name.startswith("Snap"))
    snap = f[snapshot_names[-1]]
    print(snap.name, dict(snap.attrs), list(snap.keys()))
    if "Grids" in snap:
        for name, dataset in snap["Grids"].items():
            print(name, dataset.shape, dataset.dtype)
```

## Add the existing figures and tables

Place figure files in `docs/_static/` and insert them with Markdown image
syntax. Expand the output tables using the verified dataset descriptions
from your existing guide.
