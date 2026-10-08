(numerics)=
# Numerical conventions and parallel execution

Meraxes combines per-galaxy reservoir updates with distributed mesh calculations. This page specifies the numerical representation used at commit [`90d8474`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95): units, coordinate assignment, array layout, FFT normalisation, MPI ownership, time histories and resource scaling. The physical prescriptions are given in [galaxy physics](galaxy-physics.md), [black holes](black-holes.md) and [IGM physics](igm.md).

## Unit scales and powers of the Hubble parameter

The input files supply `UnitMass_in_g`, `UnitLength_in_cm` and `UnitVelocity_in_cm_per_s`. Denote their cgs scales by $U_M$, $U_L$ and $U_V$. `set_units()` derives

```{math}
:label: num-derived-units
U_T=\frac{U_L}{U_V},\qquad
U_\rho=\frac{U_M}{U_L^3},\qquad
U_P=\frac{U_M}{U_LU_T^2},\qquad
U_{\dot u}=\frac{U_P}{U_T},\qquad
U_E=U_MU_V^2.
```

The conventional internal mass and length labels carry $h^{-1}$, where $h$ is `Hubble_h`; internal time carries the same $h^{-1}$. Consequently a rate formed as mass/time has no residual $h$ power. These dimensions should be distinguished from an output that has already been converted by its writer.

| Quantity | Conventional numerical representation | Conversion to cgs physical value |
|---|---|---|
| Mass | Internal mass number $m$ | $mU_M/h$ |
| Physical halo radius | Internal length number $r$ | $rU_L/h$ |
| Comoving position | Internal comoving coordinate $x$ | Comoving $xU_L/h$; physical $axU_L/h$ |
| Velocity | Internal velocity number $v$ | $vU_V$ |
| Time interval | Internal time number $t$ | $tU_T/h$ |
| Mass rate | Internal rate number $\dot m$ | $\dot mU_M/U_T$ |
| Physical density | Internal density number $\rho$ | $\rho U_\rho h^2$ |
| Comoving density | Comoving internal density number $\rho_c$ | Physical $\rho_cU_\rho h^2a^{-3}$ |
| Energy | Internal energy number $e$ | $eU_E/h$ |
| Pressure | Internal pressure number $p$ | $pU_Ph^2$ |

Here $a=(1+z)^{-1}$. These conversion rules describe the model's conventional internal dimensions; individual reader routines also perform format-specific conversions. In particular, the density-grid readers contain an explicit correction for the units of their expected input grids. Supplying a different input convention requires updating that reader rather than changing only an HDF5 unit label.

The configured velocity scale determines the numerical values passed to prescriptions that expect $\mathrm{km\,s^{-1}}$. The conventional mass unit is $10^{10}M_\odot$ before its $h$ conversion; it should not be confused with a grid value already expressed in $M_\odot\,\mathrm{yr^{-1}}$.

### Rates and output metadata

The catalogue and grid writers convert SFR-like internal quantities using

```{math}
:label: num-rate-output
\dot M_{\rm out}[M_\odot\,\mathrm{yr^{-1}}]
=\dot m_{\rm int}\frac{U_M}{U_T}\frac{\mathrm{seconds\ per\ year}}{M_\odot[\mathrm g]}.
```

No further $1/h$ factor belongs in this expression. Mass fields generally retain their internal numerical mass scale and advertise `v/h`; dimensionless fractions and temperatures have no $h$ conversion. A field-specific output conversion is recorded under `HubbleConversions`, alongside its `Units` attribute. The [output reference](outputs.md) lists the actual registered metadata, including case-sensitive names and omissions; metadata is not a universal substitute for the writer's implemented conversion.

The internal Hubble helper stores $H_{100}U_T$, where $H_{100}=100\,\mathrm{km\,s^{-1}\,Mpc^{-1}}$, without the factor $h$. Its physical conversion is

```{math}
:label: num-hubble-unit
H_{\rm phys}(z)=\frac{h}{U_T}H_{\rm int}(z).
```

Source: [`init.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/init.c), [`save.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/save.c), [`grid writers`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c).

## Coordinates, periodic boundaries and cell assignment

`BoxSize` is the side length $L_h$ of the periodic cube in comoving $h^{-1}\mathrm{Mpc}$. For `ReionGridDim` $N$,

```{math}
:label: num-cell-size
L=\frac{L_h}{h}\quad[\mathrm{cMpc}],\qquad
\Delta x_h=\frac{L_h}{N},\qquad
\Delta x=\frac{L_h}{hN},\qquad
\Delta x_{\rm physical}=\frac{L_h}{hN(1+z)}.
```

The coordinate helper `apply_pbc_pos()` adds or subtracts one box length when a position lies outside $[0,L_h)$. It is a one-wrap operation rather than a general modulo for arbitrarily distant coordinates. The separation helper chooses the shorter periodic displacement independently along each coordinate, then computes the Euclidean distance.

`pos_to_ngp()` assigns each coordinate to its nearest grid point:

```{math}
:label: num-ngp-index
i(x)=\operatorname{nearbyint}\!\left(\frac{Nx}{L_h}\right),\qquad
i=N\ \longrightarrow\ i=0.
```

The routine asserts a non-negative final index. `nearbyint` follows the floating-point rounding mode; it is not the same as $\lfloor Nx/L_h\rfloor$. The source's startup call uses the literal `fesetround(1)`, so its portability depends on the platform's floating-point constants and return convention. A reproduced implementation should match the actual rounding mode used by the executable rather than assume a floor-based cell origin.

For a source quantity $q_g$, `construct_baryon_grids()` deposits the cell sum

```{math}
:label: num-ngp-source
Q_{ijk}=\sum_{g\,:\,(i_g,j_g,k_g)=(i,j,k)}q_g.
```

This nearest-grid-point deposition does not distribute a galaxy among neighbouring cells. A mass/rate source grid contains a **cell sum** until the consuming routine divides by cell volume or otherwise normalises it. The dark-matter density grid is read separately; it is not constructed by summing these galaxy source properties.

Ghost and orphan galaxies with `Type < 3` participate in the galaxy-to-slab map. Their stored positions can be inherited from the last time their haloes were identified. Thus source-position updates follow the merger-tree state, rather than integrating individual galaxy orbits within the mesh.

Source: [`misc_tools.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/misc_tools.c), [`meraxes.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/meraxes.c), [`reionization.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c).

## Density-grid preparation

The selected grid reader loads the simulation's density field and, if necessary, reduces it to the reionization resolution. `calc_resample_factor()` requires the input side length in cells, $N_{\rm in}$, to be divisible by $N$. It rejects input grids coarser than the requested reionization grid.

```{math}
:label: num-grid-resample
f_{\rm resample}=\frac{N}{N_{\rm in}}\leq1,\qquad
n_{\rm every}=\frac{N_{\rm in}}{N}\in\mathbb N.
```

For $f_{\rm resample}<1$, the reader FFTs the high-resolution field, divides by its total number of cells, applies a real-space top-hat Fourier window with $R=L_h/(2N)$, inverse-transforms it, and samples every $n_{\rm every}$th grid point along each coordinate. This is smoothing followed by subsampling, rather than an arithmetic block average. High-resolution and low-resolution slabs need not belong to the same MPI rank, so sampled slices are exchanged between their owners.

After resampling, the expected density convention is converted to overdensity. Let $\rho_{\rm file}$ denote the numerical field after the reader's loading/resampling steps, $L_{\rm file}$ the box length recorded in that input format, $N_p$ the simulation particle count and $m_p$ `PartMass`. The implemented normalisation is

```{math}
:label: num-density-normalisation
C_\rho=\frac{L_{\rm file}^3h}{N_pm_p},\qquad
\delta=\max\left(C_\rho\rho_{\rm file}-1,\delta_{\rm floor}\right).
```

The ordinary single-file/`gbpTrees` paths use $\delta_{\rm floor}=-1+\mathrm{REL\_TOL}$; the VELOCIraptor multi-file path uses $-1$. The extra $h$ in $C_\rho$ is explicitly identified by the source as a correction to the expected input-density units. `deltax` stores $\delta$, so the dimensionless local density factor is $1+\delta$.

Source: [`read_grids.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids.c), [`read_grids-gbptrees.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids-gbptrees.c), [`read_grids-velociraptor.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids-velociraptor.c).

## Real, padded and complex array layouts

The final coordinate is contiguous in memory. On an MPI rank, let $i$ be the **local** first-coordinate index, $j$ the second index and $k$ the final index. `grid_index()` implements

```{math}
:label: num-grid-layout
\begin{aligned}
I_{\rm real}(i,j,k)&=k+N(j+Ni),\\
I_{\rm padded}(i,j,k)&=k+2\bigl(\lfloor N/2\rfloor+1\bigr)(j+Ni),\\
I_{\rm complex}(i,j,k)&=k+\bigl(\lfloor N/2\rfloor+1\bigr)(j+Ni).
\end{aligned}
```

| Layout | Local logical shape | Typical use |
|---|---|---|
| Real, unpadded | $(n_x,N,N)$ | `xH`, temperatures, brightness and output buffers |
| Padded real | $(n_x,N,2(\lfloor N/2\rfloor+1))$ allocated; only $N$ physical values per final row | Real inputs to in-place FFTs and source histories |
| Hermitian complex | $(n_x,N,\lfloor N/2\rfloor+1)$ | R2C Fourier coefficients |

For even $N$, the padded final dimension is $N+2$; for odd $N$, it is $N+1$. These extra values are storage padding, not spatial cells. They are removed when a padded field is written as an HDF5 cube. The allocation count returned by FFTW can exceed the simple logical complex-shape product because it includes workspace requirements; Meraxes allocates using that returned count.

The lightcone and heating-radius arrays have separate layouts:

```{math}
:label: num-special-layouts
I_{\rm LC}(i,j,k)=k+L_{\rm LC}(j+Ni),\qquad
I_{\rm heat}(r,i,j,k)=r+F\,[k+N(j+Ni)],
```

where $L_{\rm LC}$ is `LightconeLength` and $F$ is `TsNumFilterSteps`. Heating-filter index $r$ is the contiguous coordinate of the latter array. The C index helper returns `int`; grid dimensions, local counts and MPI counts must fit the source's integer indexing even where allocation sizes use `size_t` or `ptrdiff_t`.

Source: [`misc_tools.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/misc_tools.c), [`grid allocation`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c). FFTW's [real-array format](https://fftw.org/fftw3_doc/Real_002ddata-DFT-Array-Format.html) explains the Hermitian storage and padding.

## Fourier transforms and smoothing

The mesh uses single-precision FFTW (`fftwf_*`) with MPI transforms. FFTW does not normalise either direction. For a forward transform $\mathcal F$ and inverse transform $\mathcal F^{-1}_{\rm FFTW}$ on an $N^3$ mesh,

```{math}
:label: num-fft-normalisation
\mathcal F^{-1}_{\rm FFTW}[\mathcal F(q)]=N^3q,\qquad
q_R=\mathcal F^{-1}_{\rm FFTW}\!\left[W(kR)\frac{\mathcal F(q)}{N^3}\right].
```

The ionization/heating smoothing routines supply the $1/N^3$ factor before inverse-transforming. Power-spectrum calculations instead include the physical volume factor needed by their Fourier convention; see [IGM observables](igm.md). Interchanging these normalisations changes amplitudes.

For the filter helper, $L_h$ remains in internal comoving length units. It constructs

```{math}
:label: num-fft-wavevectors
\Delta k_h=\frac{2\pi}{L_h},\qquad
k_x=\begin{cases}n_x\Delta k_h,&n_x\leq\lfloor N/2\rfloor,\\(n_x-N)\Delta k_h,&n_x>\lfloor N/2\rfloor,\end{cases}
```

with the same signed mapping in $y$ and stored non-negative $k_z=n_z\Delta k_h$, $0\leq n_z\leq\lfloor N/2\rfloor$. The first-coordinate Fourier index is global, obtained by adding the slab start. The physical numerical wavenumber in $\mathrm{cMpc^{-1}}$ is $k=h k_h$.

`filter()` implements three windows:

```{math}
:label: num-filter-windows
W_0(u)=3\left(\frac{\sin u}{u^3}-\frac{\cos u}{u^2}\right),\qquad
W_1(u)=\begin{cases}1,&0.413566994u\leq1,\\0,&0.413566994u>1,\end{cases}\qquad
W_2(u)=\exp\!\left[-\frac{(0.643u)^2}{2}\right],\qquad u=k_hR_h.
```

Window `0` leaves coefficients unchanged when $u\leq10^{-4}$ rather than evaluating its small-argument expression. The sharp-$k$ and Gaussian radius factors match the volume convention used by this source. `ReionFilterType` chooses these windows for reionization filtering; density downsampling hard-codes window `0`. Radius-to-mass conventions and excursion-set thresholds are specified separately on the [IGM page](igm.md).

Without `FFTW3WisdomDir`, the persistent mesh plans use `FFTW_ESTIMATE`. A non-empty directory selects `FFTW_PATIENT` and rank/grid-specific wisdom named `fftw3f-meraxes-N_<N>-ranks_<P>.wisdom`. Rank 0 loads or saves the wisdom and distributes it to other ranks. Grid-resampling and power-spectrum temporary plans use `FFTW_ESTIMATE` in their own routines.

Source: [`reionization.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c), [`find_HII_bubbles.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/find_HII_bubbles.c), [`ComputePowerSpectrum.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/ComputePowerSpectrum.c), FFTW [transform normalisation](https://fftw.org/fftw3_doc/Multi_002ddimensional-Transforms.html).

## Two MPI decompositions

### Forest ownership for galaxies

The tree reader assigns entire merger forests to ranks. Rank 0 reads forest statistics, including counts at the last requested output and maximum contemporaneous halo/FOF counts. It sorts forests by final halo count, scans their appearance across snapshots, and assigns each newly encountered forest to the rank with the lowest accumulated final-count load.

```{math}
:label: num-forest-load
\mathrm{rank}(f)=\operatorname*{arg\,min}_r C_r,\qquad
C_{\mathrm{rank}(f)}\leftarrow C_{\mathrm{rank}(f)}+N_{\rm halo,last}(f).
```

The appearance-snapshot scan is part of the algorithm: this is not purely a global descending-size assignment performed once at the last snapshot. Forest lists are scattered to ranks and sorted locally for later searches. Storage capacity on rank $r$ is based on sums of forest maxima,

```{math}
:label: num-forest-capacity
N_{\rm halo,max,r}=\sum_{f\in r}\max_sN_{\rm halo}(f,s),\qquad
N_{\rm FOF,max,r}=\sum_{f\in r}\max_sN_{\rm FOF}(f,s).
```

These sums can exceed the maximum simultaneous count across that rank because different forests may peak at different times. The balancing metric is halo count, not measured CPU time or grid-source luminosity, so equal final counts need not yield equal runtime or peak memory.

### Slab ownership for grids

FFTW assigns each rank a contiguous range of the first mesh coordinate. `assign_slabs()` obtains local sizes from `fftwf_mpi_local_size_3d`, gathers them, and stores the rank starts. For rank $r$,

```{math}
:label: num-slab-ownership
S_r=\sum_{p<r}n_{x,p},\qquad
S_r\leq i_{\rm global}<S_r+n_{x,r},\qquad
i_{\rm local}=i_{\rm global}-S_r.
```

Galaxy/forest ownership generally differs from spatial slab ownership. `map_galaxies_to_slabs()` sorts each rank's galaxy references by the destination slab and original list index. For each property and destination rank, all forest-owning ranks build a source-contribution buffer and use `MPI_Reduce(..., MPI_FLOAT, MPI_SUM, destination_rank, ...)`. The destination converts that summed buffer to its padded local source slab.

When a galaxy needs local UVB or other grid feedback, the appropriate spatial slab is exchanged back to the forest-owning rank and sampled at its NGP position. Global summaries and source-recalibration totals use reductions across ranks. Galaxy catalogues are written per forest-owning rank; grid cubes are collectively written from spatial slabs. The master file subsequently links these products; see [output organisation](outputs.md).

Source: [`read_halos.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos.c), [`reionization.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c).

## Snapshot time and finite histories

`a_list.txt` supplies scale factors in snapshot order. Meraxes calculates $z_s=1/a_s-1$ and a lookback time by GSL quadrature,

```{math}
:label: num-lookback-time
L(z)=\frac{1}{H_{\rm int,0}}\int_{(1+z)^{-1}}^1
\frac{da}{\sqrt{\Omega_m/a+\Omega_k+\Omega_\Lambda a^2}}.
```

Here $H_{\rm int,0}=H_{100}U_T$. This expression is in the source's internal time convention; multiplying its numerical result by $U_T/h$ gives physical seconds. Forward evolution corresponds to decreasing $L$. The galaxy interval is calculated from `LastIdentSnap`, and startup enforces a single galaxy step per snapshot. [Galaxy physics](galaxy-physics.md) specifies the reservoir-update order and midpoint-burst treatment.

### Distinct history capacities

| History | Capacity/control | Representation and purpose |
|---|---|---|
| Stellar feedback | Compile-time `N_HISTORY_SNAPS`, default `17` | Per-galaxy double arrays of formed mass and initial metal mass; age/metallicity kernels provide delayed feedback |
| Heating/Ly$\alpha$/LW sources | Runtime `NstoreSnapshots_Heating` | Padded float-grid history for each enabled source channel; past snapshots supply radiative shells |
| Photometry | Compile-time `MAGS_N_SNAPS` and selected target snapshots | Stellar-luminosity histories; see [optional physics](optional-physics.md) |
| Previous brightness | Previous-snapshot real cube | Time interpolation into the lightcone |
| Persistent ionization state | Persistent current grid fields | Reionization redshift, UVB history and cumulative recombinations, rather than a complete cube for every snapshot |

The stellar-history arrays shift at snapshot reset and clear index zero. Older stellar populations also contribute to accumulated age bookkeeping outside the finite recent-history window. The feedback loader checks whether the chosen history capacity covers the table's SN-energy duration for the supplied cadence.

`set_sfr_history()` computes the heating history capacity by scanning requested evolution snapshots and the redshift reach of its radial shells. It is therefore not set by `N_HISTORY_SNAPS`. Each current source grid becomes history slot zero; older slots shift by one. Recalibration modifies the current slot, while older slots retain the recalibration applied when they were created.

### Thermal update and lightcone time

`ComputeTs()` uses $\Delta z=z_s-z_{s-1}<0$ and an explicit update of the returned redshift derivatives:

```{math}
:label: num-thermal-update
x_e^{\rm new}=x_e^{\rm old}+\left(\frac{dx_e}{dz}\right)_s\Delta z,\qquad
T_K^{\rm new}=T_K^{\rm old}+\left(\frac{dT_K}{dz}\right)_s\Delta z.
```

An electron fraction above one is reset to $1-\mathrm{FRACT\_FLOAT\_ERR}$, while a negative value is reset to zero. Heating updates are skipped if the current temperature is already at least `MAX_TK`. A computed temperature below `MIN_TK` is reset to the CMB temperature at that redshift, rather than clamped to `MIN_TK` itself. The physical derivatives and spin-temperature calculation are given under [IGM physics](igm.md). These finite-step treatments make snapshot cadence part of the numerical specification.

The radiation/lightcone helper `gettime(z)` uses a distinct cosmic-time expression,

```{math}
:label: num-cosmic-time-helper
t_{\rm helper}(z)=\frac{2\sqrt{1+\Omega_m/\Omega_\Lambda}}{3H_{100}h}
\operatorname{asinh}\!\left[\sqrt{\frac{\Omega_\Lambda}{\Omega_m}}(1+z)^{-3/2}\right].
```

For flat matter-plus-$\Lambda$ cosmology this is the usual cosmic-time relation. It does not include an independent curvature term. Lightcone interpolation is linear in this time coordinate between neighbouring coeval cubes, with periodic reuse along the line of sight; it is not linear interpolation in redshift.

Source: [`init.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/init.c), [`galaxies.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/galaxies.c), [`ComputeTs.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/ComputeTs.c), [`XRayHeatingFunctions.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/XRayHeatingFunctions.c), [`ConstructLightcone.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/ConstructLightcone.c).

## Precision and reproducibility

The generic `interp()` helper linearly interpolates a table and aborts outside its tabulated domain. `trapz_table()` adds the trapezoidal contributions of traversed intervals, linearly interpolating the endpoints when the integration boundary cuts an interval:

```{math}
:label: num-table-integration
y(x)=y_i+\frac{y_{i+1}-y_i}{x_{i+1}-x_i}(x-x_i),\qquad
\int_a^b y(x)\,dx\simeq\sum_j\frac{y(x_{j+1})+y(x_j)}{2}(x_{j+1}-x_j).
```

The sum includes the clipped interval endpoints $a$ and $b$. Individual cooling, modifier and thermal-table routines can have their own clamping or extrapolation rules; those are described with the corresponding prescriptions rather than inferred from this generic helper.

Galaxy reservoir arithmetic and many accumulators use `double`; source meshes, FFTs and most stored grid products use `float`. Some output catalogue fields are also explicitly cast to float. The source's general tolerances are `REL_TOL=1e-5` and `ABS_TOL=1e-8`; individual physical routines have additional thresholds and clamps.

The float-comparison helper follows

```{math}
:label: num-close-tolerance
\operatorname{isclose}(a,b)\iff |a-b|\leq\epsilon_{\rm abs}+\epsilon_{\rm rel}|b|,
```

using $\epsilon_{\rm abs}=10^{-8}$ and $\epsilon_{\rm rel}=10^{-5}$ if negative tolerance arguments request its defaults. This is asymmetric in its relative reference value $b$.

`init_meraxes()` creates the GSL `ranlxd1` generator and initialises it with `RandomSeed` on each rank. Escape-fraction scatter and stochastic black-hole choices consume this rank-local stream. Holding the seed fixed alone does not assign an immutable random value to each galaxy: changing rank count, forest assignment or enabled random-draw branches can change the sequence consumed by an individual object. The source also calls `srand(time(NULL))` for a separate standard-library generator.

Floating-point addition is non-associative. Source construction reduces float buffers with MPI, and changing decomposition or reduction order can alter low-order bits. FFT planning and platform libraries can also change numerical roundoff. The presence of `accurate_sumf()`, which sorts floats and accumulates them in double, does not mean every mesh/reduction uses that routine.

For a reproducible run record, retain the commit and dirty diff, all effective parameters, build options, table/input versions, snapshot list, compiler/library versions, MPI rank count, seed and FFTW wisdom choice. The master output stores effective parameters and git information, but a full run record also needs the external input and build identity.

Source: [`init.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/init.c), [`misc_tools.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/misc_tools.c), [`blackhole_feedback.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/blackhole_feedback.c), [`save.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/save.c).

## Resolution and resource scaling

The finite periodic mesh sets the fundamental and axial Nyquist wavenumbers:

```{math}
:label: num-resolution-scales
k_{\rm fund}=\frac{2\pi}{L},\qquad
k_{\rm Nyquist}=\frac{\pi N}{L}.
```

Neither finer mesh resolution nor more MPI ranks resolves galaxies below the mass resolution of the input trees. NGP deposition introduces a cell-scale assignment window and aliasing; the current power-spectrum routine does not divide by an NGP deconvolution window. Reionization/heating filtering and halo resolution should therefore be varied independently when establishing numerical convergence. Time convergence requires a sufficiently fine input snapshot cadence, rather than increasing `NSteps` in this source version.

Let $n_{R,r}=n_{x,r}N^2$ be local physical-cell count and $n_{C,r}$ the complex allocation count returned by FFTW. The principal array memory scales are

```{math}
:label: num-grid-memory
\begin{aligned}
B_{\rm real,r}&=4n_{R,r},&
B_{\rm padded,r}&=8n_{C,r},&
B_{\rm complex,r}&=8n_{C,r},\\
B_{\rm history,r}&=8n_{C,r}H,&
B_{\rm smooth,r}&=8n_{R,r}F,&
B_{\rm LC,r}&=4n_{x,r}NL_{\rm LC}.
\end{aligned}
```

These are bytes per real float field, padded float field, complex float field, $H$-snapshot padded history, double heating-radius array, and float lightcone respectively. They describe arrays, not the complete job allocation. Each source channel can require current, Fourier, filtered, historical and smoothed copies. Grid readers and writers allocate additional temporary buffers; FFTW plans and communication add overhead.

Ignoring allocation/workspace overhead, a complete unpadded float cube is $4N^3$ bytes. Doubling $N$ multiplies one cube's memory and output size by eight. FFT work grows approximately as $N^3\log N$, while repeated filtering adds a factor set by the number of radii. That scaling is a numerical estimate from the transform and allocation structure, not a measured timing guarantee.

Galaxy-side memory additionally scales with local galaxy count and the compile-time structure size:

```{math}
:label: num-galaxy-memory
B_{\rm galaxies,r}\simeq N_{\rm galaxies,r}\,\mathrm{sizeof}(\texttt{galaxy\_t}),\qquad
B_{\rm recent\ histories,r}=16H_{\rm SN}N_{\rm galaxies,r}
```

for the two baseline double arrays `NewStars` and `NewMetals`. Optional Population III, photometry and source treatments enlarge the structure further. Halo/FOF storage follows forest-capacity sums rather than exactly the current count. The source-construction scratch buffer is sized for the largest spatial slab and is allocated on each rank.

Ordinary execution stores one halo snapshot at a time. Interactive/MCMC storage modes retain halo snapshots through the last requested output and can cache density/velocity slabs, increasing memory with the number of retained snapshots. These code paths are described in [workflow](workflow.md); memory comparisons must use the same execution mode and enabled physics.

The allocation routines and `log_memory_usage()` provide the basis for diagnosing actual resource use. A complete estimate must count enabled source channels, heating history length, filter radii, lightcone length, halo/galaxy capacity and temporary I/O arrays; counting only the saved output cubes omits most working memory.

Source: [`reionization.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c), [`read_halos.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos.c), [`read_grids.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_grids.c), [`meraxes.h`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/meraxes.h), [`CMakeLists.txt`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/CMakeLists.txt).
