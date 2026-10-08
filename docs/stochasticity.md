(stochasticity)=
# Stochastic radiation sources

Meraxes can modify the stellar escape fraction, replace the SFR used by
radiation sources with a median relation, and scatter the stellar X-ray
luminosity. These prescriptions construct **radiation-source fields** alongside
the ordinary galaxy properties. They do not directly replace the physical cold
gas, stellar mass or star-formation history evolved by the galaxy model.
Radiation feedback can subsequently change those properties through the coupled
IGM calculation.

This page documents `forests` at
[`90d8474cf41dcea646189fb86a65b7e18755ed95`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95).
Branch-specific treatments are described from this source revision. See
[Getting started](getting-started.md) for compilation,
[Inputs](inputs.md) for parameter-file precedence and units,
[IGM physics](igm.md) for the radiation solver,
[Outputs](outputs.md) for field names, and [References](references.md) for the
published model foundations.

## Controls and defaults

The compile-time gate is `USE_STOCHASTICITY`, a CMake option with default `OFF`.
`USE_MINI_HALOS` defaults to `OFF`; with it disabled every galaxy is treated as
Pop. II. Enabling it adds population-specific stellar source histories and
median-SFR tables. There is no `USE_SFR_INTEGRATION` CMake option or conditional
source pathway in this revision.

| Runtime parameter | Default | Implemented role |
|---|---:|---|
| `EscapeFracDependency` | `1` | Escape-fraction selector 0–6, defined below. |
| `EscapeFracNorm` | `0.06` | Pop. II stellar escape-fraction normalization. |
| `EscapeFracNormIII` | `0.06` | Pop. III normalization in minihalo builds. |
| `EscapeFracRedshiftOffset` | `6.0` | Denominator of the redshift factor. |
| `EscapeFracRedshiftScaling` | `0.5` | Redshift exponent. |
| `EscapeFracPropScaling` | `0.5` | Galaxy-property exponent. |
| `EscapeFracScatterDex` | `0.0` | Scatter width in log10 stellar escape fraction; active only if greater than `ABS_TOL = 1e-8`. |
| `Flag_RemoveSFRScatter` | `0` | Set exactly `1` to construct median-SFR radiation sources. |
| `XrayScatterDex` | `0.0` | Scatter width in log10 Pop. II stellar X-ray luminosity; active if greater than zero. |
| `Flag_SourceRecalibration` | `0` | Non-zero enables the applicable source-budget rescalings. |
| `Flag_InstantaneousSFR` | `1` | Non-zero uses snapshot SFR for heating sources; zero uses gross stellar mass divided by the smoothing timescale. |
| `ReionSfrTimescale` | `0.5` | Smoothing timescale in units of the snapshot Hubble time. |
| `LXrayGal` | `3.16e40` | Pop. II soft-band luminosity per SFR, in erg s−1/(solar masses yr−1). |
| `LXrayGalIII` | `3.16e40` | Corresponding Pop. III normalization. |
| `Flag_IncludeSpinTemp` | `0` | Enables the heating, Ly-alpha and spin-temperature calculation; required for the stellar X-ray source-grid pathway. |
| `RandomSeed` | `1809` | Seed of the shared GSL random-number generator on each MPI rank. |
| `NSteps` | `1` | Current runtime requires exactly one galaxy-physics step per snapshot. |

The stellar X-ray spectral controls retain their ordinary meanings:
`SpecIndexXrayGal = 1`, `SpecIndexXrayIII = 1`, `NuXrayThreshold = 500 eV`,
`NuXraySoftCut = 2000 eV`, and `NuXrayMax = 10000 eV`. Scatter changes the
luminosity normalization, not these spectral shapes. AGN luminosities and
escape fractions have separate controls; they are not perturbed by
`EscapeFracScatterDex` or `XrayScatterDex`.

Defaults and accepted parameter names are taken from
[defaults.par](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/input/params/defaults.par),
[read_params.c](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_params.c)
and [CMakeLists.txt](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/CMakeLists.txt).

## Ordinary and treated source pathways

`construct_baryon_grids()` deposits eligible galaxies onto the radiation grid
with nearest-grid-point assignment. Its source choices are:

| Radiation input | Ordinary source | Treated source |
|---|---|---|
| Cumulative stellar ionizing source (`prop_stellar`) | `FescWeightedGSM`. | `StochasticityTreatedFescWeightedGSM` when escape scatter is active or noSFR equals 1; optional GSM factor. |
| Snapshot escaped stellar rate (`prop_weighted_sfr`) | `FescWeightedSfr`. | `StochasticityTreatedFescWeightedSfr` under the same condition; optional weighted-SFR factor. |
| Unweighted stellar SFR (`prop_sfr`) | `Sfr`, or `GrossStellarMass / t_SFR` in the smoothed mode. | The corresponding noSFR source quantity; optional global Ly-alpha factor. Escape-fraction scatter alone does not alter this field. |
| Stellar X-ray luminosity (`prop_xray_luminosity`, stochasticity build) | `LXrayGal` times the selected ordinary SFR. | The noSFR luminosity when requested, then an X-ray draw when requested, then the optional global X-ray factor. |
| Pop. III stellar inputs | Analogous `FescIIIWeightedGSM`, `FescIIIWeightedSfr` and `SfrIII`. | Analogous treated escaped fields and noSFR SFR/mass, with the population-specific qualifications described below. |
| AGN sources | Effective BH and AGN luminosity fields. | These fields retain their separate AGN prescriptions. |

The compiled stochasticity path constructs the dedicated Pop. II X-ray
luminosity field even when its scatter width is zero. Without that compiled
path, stellar heating uses the ordinary SFR field and luminosity normalization.

## Deterministic escape fraction

Let $z$ be snapshot redshift, $h$ the dimensionless Hubble parameter,
$f_{\rm norm,p}$ the normalization for population $p$, $\beta$ the redshift
exponent, and $\alpha$ the property exponent. Before CGM attenuation and
clipping, the positive-property branch is

```{math}
:label: stoch-fesc-relation
f_{\rm esc,p}^{\rm pre}
=f_{\rm norm,p}R_d(z)P_{d,p}^{\alpha},\qquad
R_d(z)=
\begin{cases}
1,&d=0,\\
[(1+z)/z_{\rm off}]^{\beta},&1\leq d\leq6,
\end{cases}
```

where $d$ is `EscapeFracDependency`, $z_{\rm off}$ is
`EscapeFracRedshiftOffset`, and the property factor $P_{d,p}$ is below.
Setting $\beta=0$ removes the redshift dependence. For $d=0$ or 1 there is no
property factor. The following formulas reproduce the **internal quantities
actually passed to `pow()`**, including their normalization.

| Selector | Property factor | Non-positive-property behavior |
|---:|---|---|
| `0` | None; normalization only. | Not applicable. |
| `1` | None; redshift factor only. | Not applicable. |
| `2` | `StellarMass / h`. This uses the internal mass value, equivalent to stellar mass in units of $10^{10}$ solar masses. Pop. III uses the same total `StellarMass`. | Escape fraction is set to 1 before CGM attenuation. |
| `3` | Population SFR converted to solar masses yr−1. | Escape fraction is set to 0. |
| `4` | $(\mathrm{ColdGas}/\mathrm{DiskScaleLength}^{2})\,0.01h/10$. This is the implemented surface-density proxy; it contains no additional disk-area factor. | Escape fraction is set to 1 if gas mass or disk scale length is non-positive. |
| `5` | `Mvir / h`, equivalent to virial mass in units of $10^{10}$ solar masses. | Escape fraction is set to 1. |
| `6` | $(\mathrm{Sfr}_p/\mathrm{StellarMass})\,(100\,\mathrm{SEC\_PER\_MEGAYEAR}/\mathrm{UnitTime\_in\_s})$. This equals physical specific SFR in units of $10\,\mathrm{Gyr}^{-1}$. | Escape fraction is set to 0 if SFR or total stellar mass is non-positive. |

For selectors 3 and 6, Pop. III uses `SfrIII`; selector 6 still divides by the
total `StellarMass`. An unrecognized selector reaches an error-reporting branch;
use only the documented values 0–6.

If `Flag_FescCGMSuppression > 0` and the stored `tau_cgm > 0`, the stellar
escape fraction is multiplied by $\exp(-\tau_{\rm CGM})$. The deterministic
value is then clipped:

```{math}
:label: stoch-fesc-clamp
f_{\rm esc,p}^{0}
=\min\!\left[1,\max\!\left(0,
 f_{\rm esc,p}^{\rm pre}e^{-\tau_{\rm CGM}}\right)\right].
```

Use $\tau_{\rm CGM}=0$ when attenuation is inactive. The separate BH escape
fraction is $\mathrm{EscapeFracBHNorm}[(1+z)/6]^{\mathrm{EscapeFracBHScaling}}$,
clipped to [0,1]; its default normalization and exponent are 1 and 0.

### Optional CGM attenuation

The attenuation controls default to `Flag_FescCGMSuppression = 0`,
`FescCGMSuppressionNorm = 0.00008`, `FescCGMSuppressionScaling = 0.2` and
`FescCGMGamma12Scaling = 6.0`. For positive `HotGas` and `Rvir`, the grid-to-galaxy
assignment computes

```{math}
:label: stoch-cgm-optical-depth
\tau_{\rm CGM}
=A_{\rm CGM}
\left(\frac{M_{\rm hot}}{10^{8}\,M_\odot}\right)^a
\left(\frac{10\,\mathrm{kpc}}{R_{\rm vir}}\right)^{2a}S^b.
```

Here $M_{\rm hot}$ and $R_{\rm vir}$ are physical hot-gas mass and virial
radius; $A_{\rm CGM}$, $a$ and $b$ are the three controls above. The modulation
$S$ is $10\Gamma_{12}$ in mode 1, the code accumulator of
$\Gamma_{12}\Delta t_{\rm Myr}$ in mode 2, or the local clumping factor in
mode 3. The sampled Gamma12 grid value is multiplied by $h^2$ before these
operations, and negative drivers are set to zero. Mode 2's
`cumulative_ionization` is reset each snapshot by `reset_galaxy_properties()`;
it is not an uninterrupted integral over the simulation's entire history.
The source uses previously assigned galaxy/grid quantities according to the
[execution workflow](workflow.md).

Source: [escape-fraction update and grid sampling](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c)
and [snapshot resets](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/galaxies.c).

## Escape-fraction scatter and source accumulation

The scatter helper draws one uniform variate $u$ from the rank's GSL generator
and sets $g=\Phi^{-1}(u)$, where $\Phi$ is the standard-normal cumulative
probability. For positive input $q$ and width $\sigma>0$ in dex,

```{math}
:label: stoch-lognormal
q^{\rm draw}=q\,10^{\sigma g},\qquad
 g\sim\mathcal N(0,1),\qquad s=(\ln10)\sigma.
```

The helper returns the input unchanged if the width or input is non-positive.
Its argument is named `mean_esc` in the implementation, but a positive input is
the distribution's **median**, not its arithmetic mean. Before clipping,
$\mathbb E[q^{\rm draw}]=q\exp(s^2/2)$. No compensating shift is applied to keep
the mean fixed.

For stellar escape fractions the input is the already clipped deterministic
$f_{\rm esc}^{0}$, and the draw is clipped again to [0,1]. For
$0<f_{\rm esc}^{0}\leq1$ and $s>0$, the implemented distribution therefore has
mean

```{math}
:label: stoch-clipped-mean
\mathbb E[f_{\rm esc}^{\rm draw,clipped}]
=f_{\rm esc}^{0}e^{s^2/2}
 \Phi\!\left(\frac{\ln(1/f_{\rm esc}^{0})-s^2}{s}\right)
 +1-\Phi\!\left(\frac{\ln(1/f_{\rm esc}^{0})}{s}\right).
```

This is the analytic expectation of the implemented clipped lognormal, rather
than a separately calibrated physical relation. At the upper boundary the
clipped mean can fall below the deterministic value. The positive-width
prescription is sampled at each relevant `update_galaxy_fesc_vals()` call;
it does not cache one lifetime draw per galaxy.

The ordinary fields `Fesc`/`FescIII` retain the deterministic value. A
star-formation update with newly formed mass $\Delta M_{\star,j}$ and current
snapshot-local SFR accumulator $\dot M_{\star,j}$ adds

```{math}
:label: stoch-source-accumulators
G\leftarrow G+\Delta M_{\star,j}f_j,\qquad
W\leftarrow W+\dot M_{\star,j}f_j.
```

Here $G$ is `FescWeightedGSM`, $W$ is `FescWeightedSfr`, and $f_j$ is the
ordinary deterministic value. The corresponding
`StochasticityTreatedFescWeightedGSM`/`StochasticityTreatedFescWeightedSfr`
accumulate the same terms with the scattered value. Pop. III has analogous
fields. $G$ is a cumulative escaped stellar-source mass, not surviving stellar
mass; $W$ is the source code's snapshot-local accumulator. Because the update
uses the current accumulated `Sfr`, $W$ should not be assumed to equal final
`Sfr * Fesc` when several star-formation updates occur within a snapshot.

Source: [scatter helper](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/misc_tools.c),
[escape-fraction updates](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c)
and [star-formation call sites](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/star_formation.c).

## Median-SFR radiation sources: noSFR

`Flag_RemoveSFRScatter = 1` replaces radiation-source SFRs by a deterministic
relation at fixed current halo mass, galaxy type and stellar population.
It does not remove scatter from the physical galaxy catalogue. Its algorithm
is run inside `construct_baryon_grids()` after galaxy evolution.

### Distributed median construction

The table has three galaxy-type rows (0: central, 1: resolved satellite,
2: orphan) and 376 halo-mass grid nodes. In internal `Mvir` units,

```{math}
:label: stoch-mass-grid
x=\log_{10}(\mathrm{Mvir}),\qquad
x_i=-3.50+0.02i,\qquad i=0,\ldots,375.
```

This covers $\log_{10}[M_{\rm vir}/(M_\odot/h)]=6.50$ to 14.00.
Assignment uses $i=\lfloor(x+3.50)/0.02\rfloor$, with values below/above the
range placed at the first/last node. The source binning assumes finite,
positive `Mvir`; it does not locally validate that precondition before taking
the logarithm.

For each population and `[Type, mass-bin]` cell, the fitting sample consists of
eligible galaxies with `0 <= Type <= 2` and strictly positive, finite SFR.
There is no additional `GhostFlag` exclusion. With minihalos enabled, fitting
uses only galaxies currently in the requested `Galaxy_Population`, and uses
`Sfr` for Pop. II or `SfrIII` for Pop. III.

All ranks count and gather their **individual log10 SFR samples** with
`MPI_Gather`/`MPI_Gatherv`. Rank 0 sorts the combined samples per cell and takes
the median. For an even sample size, it averages the two central logarithms,
so exponentiating gives their geometric mean. This is not a median of
rank-local medians. `NO_SFR_SFR_MIN_COUNT = 1` makes every occupied cell valid.
The final float table is broadcast to every rank.

For each type independently, gaps between valid nodes are linearly
interpolated in log SFR. Nodes outside the populated interval receive the
logarithmic floor −30 (`NO_SHMR_LOG10_SFR_FLOOR`); an entirely empty type row
receives that floor everywhere. The historical macro name does not change
this SFR-based algorithm.

At a galaxy's mass, two usable neighboring table values $y_i,y_{i+1}$ give

```{math}
:label: stoch-sfr-interpolation
\dot M_\star^{\rm src}=10^{(1-w)y_i+wy_{i+1}},\qquad
w=\frac{x-x_i}{0.02}.
```

Here $y_i$ is the completed table of log10 internal SFRs. Endpoint masses use
the endpoint value. If the left value is at the floor, the returned SFR is
$10^{-30}$; if only the right value is at the floor, the left value is held
constant instead of interpolating toward the empty region. An object whose
original SFR is non-positive receives **zero**, independently of this floor.
Thus noSFR retains the original active/inactive distinction.

### Cumulative treated source history

Let $M_{\star,g}^{\rm src}$ denote the cumulative `GrossStellarMassNoScatter`
for galaxy $g$. Each noSFR construction adds

```{math}
:label: stoch-treated-gsm
\Delta M_{\star,g}^{\rm src}
=\dot M_{\star,g}^{\rm src}\Delta t_g,\qquad
M_{\star,g}^{\rm src}\leftarrow
 M_{\star,g}^{\rm src}+\Delta M_{\star,g}^{\rm src},
```

where $\Delta t_g$ is `gal->dt` and both operands use compatible internal
units. The current supported run has `NSteps = 1`. This is a per-galaxy
integration during source-grid construction, not an integration of an output
grid or a fresh median relation for cumulative stellar mass.

A temporary copy of the galaxy receives this source cumulative mass and SFR,
sets `StellarMass` to the cumulative source mass, retains the previously treated
escaped cumulative history, and calls `update_galaxy_fesc_vals()`.
Consequently the escape-fraction selectors involving stellar mass or SFR are
evaluated on these source properties. Halo mass, cold gas and disk properties
remain those of the physical galaxy. The resulting deterministic escaped
source increments populate the treated GSM and weighted-SFR fields. The
original physical and source fields remain separately available.

`SfrNoScatter` and treated weighted SFR reset each snapshot; treated gross
stellar mass and escaped GSM persist. Mergers add both ordinary and treated
cumulative histories to the surviving parent, including Pop. III histories.
A Pop. II parent can therefore retain a Pop. III escaped source budget after
a population transition or merger. Median-table fitting uses current
population, whereas cumulative-budget recalibration includes retained
population histories.

Source: [Stochasticity.h](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/Stochasticity.h),
[median construction and treatment](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/Stochasticity.c),
[snapshot resets](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/galaxies.c)
and [merger inheritance](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/mergers.c).

## Stellar X-ray luminosity scatter

For Pop. II, the source rate used by the stellar X-ray grid is

```{math}
:label: stoch-xray-source-sfr
\dot M_{\star,X}=
\begin{cases}
\dot M_\star,&\mathrm{Flag\_InstantaneousSFR}\ne0,\\
M_\star^{\rm gross}/t_{\rm SFR},&\mathrm{Flag\_InstantaneousSFR}=0,
\end{cases}
\qquad
t_{\rm SFR}=\mathrm{ReionSfrTimescale}\,t_H(z).
```

Here $t_H(z)$ is the Hubble time returned by the source's `hubble_time()`,
$M_\star^{\rm gross}$ is cumulative gross stellar mass, and the resulting rate
is converted to solar masses yr−1. noSFR substitutes its source SFR or source
gross stellar mass into the same calculation. With $\mathcal L_X$ equal to
`LXrayGal`,

```{math}
:label: stoch-xray-luminosity
L_X^0=\mathcal L_X\dot M_{\star,X},\qquad
L_X^{\rm draw}=L_X^0\,10^{\sigma_Xg}.
```

$L_X$ is in erg s−1 and $\sigma_X$ is `XrayScatterDex`. The dedicated grid
stores $L_X/10^{40}\,\mathrm{erg\,s}^{-1}$, using
`XRAY_LUMINOSITY_UNIT = 1e40`. X-ray draws are not clipped at an upper bound.
Their input normalization is therefore the lognormal median, with the same
unclipped mean enhancement given above. Zero luminosities remain zero.
Each eligible galaxy is drawn when its luminosity is deposited during source
construction; past heating-history slots preserve their previously generated
fields rather than being redrawn at every later snapshot.

This dedicated luminosity/scatter pathway is Pop. II only. Pop. III heating
continues to use the `sfrIII` history and `LXrayGalIII`; `XrayScatterDex` is not
applied to that separate population field. The AGN hard/soft X-ray histories
are also separate. Setting an X-ray width without enabling spin-temperature
calculations does not produce an X-ray heating calculation.

Source: [luminosity construction and history deposition](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c)
and [heating-source consumption](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/ComputeTs.c).

## Snapshot source recalibration

`Flag_SourceRecalibration` rescales radiation fields against the **untreated
source budgets in the same evolving run**. It does not read an external
fiducial history and does not guarantee agreement with a separate run whose
feedback has evolved different galaxies.

For a source quantity $Q$, define its untreated target $T_Q$ and treated raw
budget $R_Q$ over the specified galaxies or mass cell. A supported positive
budget uses

```{math}
:label: stoch-recalibration
C_Q=T_Q/R_Q,\qquad Q^{\rm grid}=C_QQ^{\rm treated}.
```

The factors are calculated from MPI-summed budgets, and are applied on
**deposition**. They do not rewrite the stored per-galaxy histories or clip an
individual rescaled escape fraction. Factors may exceed one.

| Field or budget | Activation with `Flag_SourceRecalibration != 0` | Scope and target |
|---|---|---|
| Stellar escaped GSM and weighted SFR with escape-fraction scatter | `Flag_RemoveSFRScatter == 0` and `EscapeFracScatterDex > 1e-8` | Separate global GSM and weighted-SFR factors for Pop. II and, if compiled, Pop. III; targets are ordinary escaped accumulators. |
| Stellar escaped GSM and weighted SFR with noSFR | `Flag_RemoveSFRScatter == 1` | Separate factors per `[Type, halo-mass-bin]` and population, using the same 376-node grid; targets are ordinary escaped accumulators. |
| Pop. II stellar X-ray luminosity | `Flag_RemoveSFRScatter == 1` **or** `XrayScatterDex > 0` | One global factor; target luminosity comes from the untreated galaxy SFR/gross stellar mass. Requires the spin-temperature source-grid path. |
| Pop. II unweighted SFR, used for stellar Ly-alpha | `Flag_RemoveSFRScatter == 1` | One global factor; target is untreated SFR or gross stellar mass according to `Flag_InstantaneousSFR`. The smoothed mode is divided by the common timescale after deposition. |

The GSM factors include all eligible type-0–2 galaxies carrying a positive
ordinary or treated history for the population being calibrated, regardless
of their **current** population. noSFR instantaneous weighted-SFR budgets
additionally require current membership of that population. The Pop. III
unweighted `sfrIII` branch does not receive the separate global Pop. II
Ly-alpha or X-ray factors listed above.

There are two different zero-budget policies in the implementation:

| Routine | Zero-budget and invalid-budget behavior |
|---|---|
| Escape-fraction global factors | Reject non-finite or negative target/raw budgets. If raw ≤ `ABS_TOL`, return 1 when target ≤ `ABS_TOL`; otherwise abort because the positive target cannot be restored. Reject non-finite or negative factors. |
| noSFR cell factors and global X-ray/Ly-alpha factors | Reject non-finite or negative target/raw budgets. Use target/raw if raw > 0; otherwise return 1, including a positive target with zero raw. Reject a non-finite factor, or a factor numerically equal to zero when the target is positive. |

The second policy leaves unsupported zero-source cells/fields unchanged; it
does not manufacture sources to meet a positive target. GSM and weighted-SFR
factors are independent: matching cumulative escaped source mass does not
imply that instantaneous escaped SFR is matched by the same factor.
Heating-history arrays shift their older slots before construction; current
X-ray/Ly-alpha factors scale only the newly constructed slot. Older slots
retain the factors applied at their own construction times.

Source: [budget reductions and guard conditions](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/Stochasticity.c)
and [activation conditions and grid scaling](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/reionization.c).

## Valid combinations and runtime checks

Use non-negative, finite scatter widths and 0/1 values for the source flags.
The parameter reader does not supply general finite-value or sign validation
for these widths. In particular, several noSFR construction branches test
**exactly** `== 1`, whereas startup conflict checks test `!= 0`; other integer
values are not alternative treatment modes.

| Requested combination | Current behavior |
|---|---|
| All treatment widths/flags zero, either build | Ordinary radiation sources; valid. |
| Any positive active width, non-zero noSFR flag or non-zero recalibration, with `USE_STOCHASTICITY=OFF` | Startup abort. |
| Escape-fraction scatter alone | Valid with stochasticity compiled; recalibration optional. |
| noSFR alone | Valid with stochasticity compiled; recalibration optional. |
| X-ray scatter alone | Valid with stochasticity compiled; recalibration optional; enable spin temperature for heating. |
| Escape-fraction scatter + X-ray scatter | Allowed; stellar and X-ray recalibrations act separately if enabled. |
| Escape-fraction scatter > `ABS_TOL` + non-zero noSFR | Startup abort: choose one stellar treatment. |
| X-ray scatter > 0 + non-zero noSFR | Allowed with a startup warning that a noSFR source model with X-ray scatter must be intended. |
| Recalibration enabled with escape scatter ≤ `ABS_TOL`, X-ray scatter ≤ 0 and noSFR = 0 | Startup abort: no active treatment to calibrate. |
| `NSteps != 1` | Startup abort for the current model. |
| Spin temperature + CUDA | Startup abort; spin-temperature features are unavailable in the CUDA path. |
| Spin temperature + `FlagMCMC != 0` | Startup abort because the required SFR-grid histories must be stored. |

Median gathering also aborts on allocation failure or if local/global sample
counts exceed the `MPI_Gatherv` integer-count limit (`INT_MAX`). This
implementation gathers individual samples to rank 0, so its root-memory
requirement grows with the number of active galaxies, rather than only with
the fixed table size.

## Portable configuration examples

From an already prepared checkout, configure a CPU build that includes the
prescriptions:

```sh
cmake -S . -B build-stochastic -DUSE_STOCHASTICITY=ON -DUSE_MINI_HALOS=OFF
cmake --build build-stochastic --parallel
cp build-stochastic/input.par run.par
```

Adapt the generated `run.par` to an available simulation following
[Inputs](inputs.md). The following are **overrides to that configured input**,
not complete independent parameter files. Preserve its simulation and physical
table paths. Choose one stellar treatment:

```text
# Escape-fraction scatter around a halo-mass relation
EscapeFracDependency      : 5
EscapeFracRedshiftScaling : 0.0
EscapeFracPropScaling     : 0.5
EscapeFracScatterDex      : 0.3
Flag_RemoveSFRScatter     : 0
XrayScatterDex            : 0.0
Flag_SourceRecalibration  : 1
NSteps                    : 1
RandomSeed                : 1809
```

or

```text
# Median-SFR stellar sources
EscapeFracScatterDex      : 0.0
Flag_RemoveSFRScatter     : 1
XrayScatterDex            : 0.0
Flag_SourceRecalibration  : 1
NSteps                    : 1
RandomSeed                : 1809
```

To include a stellar X-ray scatter experiment, set `XrayScatterDex` to the
chosen positive width and enable the heating path:

```text
Flag_PatchyReion          : 1
ReionUVBFlag              : 1
Flag_IncludeSpinTemp      : 1
Flag_InstantaneousSFR     : 1
XrayScatterDex            : 0.3
```

The normal coupled path calls `call_ComputeTs()` before the HII solver and
constructs the baryon/source grids there; the HII wrapper reuses them. With
spin temperature disabled, the HII wrapper constructs them itself. Use
`Flag_ReionizationModifier = 1` for the ordinary coupling of the patchy
photoheating field to galaxy infall. Source treatment and galaxy-infall
feedback are separate choices; their interaction is described in
[IGM physics](igm.md). This example uses the ordinary non-zero UVB pathway,
which performs radiation construction throughout the active calculation.

Launch with the MPI implementation used by the build:

```sh
mpiexec -n 4 ./build-stochastic/bin/meraxes run.par
```

## Random streams, MPI and reproducibility

Initialization allocates `gsl_rng_ranlxd1` and seeds it with `RandomSeed` on
**every** rank. The seed is not offset by rank, and scatter is not an
ID-hashed per-galaxy random field. Escape-fraction and X-ray draws consume the
same generator also used by other GSL-based random choices in the model.
The separate C-library `srand(time(NULL))` initialization is not the generator
used by these lognormal draws.

A repeated run must preserve the source revision, parameter values, build
settings, input trees, forest selection/distribution and MPI rank count to
reproduce the draw sequence and reduction order. Changing MPI decomposition,
galaxy traversal, enabled prescriptions or other generator consumers can
assign different draws to a given galaxy even when `RandomSeed` is unchanged.
MPI sums and float grid deposition can also change last-bit results with
reduction order. The distributed median combines all individual samples, so
its statistical definition does not depend on a median-of-rank-medians
approximation; this does not make the full simulation independent of MPI
layout.

Record the executable's printed Git revision, build options, complete resolved
parameters, data identifiers, MPI rank count and seed with a run. The ordinary
`Fesc` catalogue column alone does not reveal its stochastic escape-fraction
draws; verify the treated radiation grids and their source-budget diagnostics
using [Outputs](outputs.md).

Source: [RNG initialization](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/init.c),
[scatter draw](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/misc_tools.c)
and [MPI construction](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/Stochasticity.c).
