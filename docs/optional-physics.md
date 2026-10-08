# Population III stars, metal enrichment and synthetic observables

This page describes the optional mini-halo/Population III model and the synthetic stellar-continuum and [O III] observables. These extensions share the galaxy evolution machinery described in [galaxy physics](galaxy-physics.md), the radiation transport in [IGM physics](igm.md) and the output conventions in [outputs](outputs.md).

[Ventura et al. (2024)](https://doi.org/10.1093/mnras/stae567) describe the resolved mini-halo and external-enrichment development. [Ventura et al. (2025)](https://doi.org/10.1093/mnras/staf699) develop a large-volume, unresolved Pop. III radiation prescription. The latter paper is scientific context: enabling `USE_MINI_HALOS` does not by itself implement or calibrate its unresolved-source scaling relations.

## Feature controls

| Feature | Build/runtime control | Main implementation |
|---|---|---|
| Separate Pop. II/III populations and molecular cooling | `USE_MINI_HALOS` | `src/core/PopIII.c`; population-specific branches in galaxy physics |
| Lyman–Werner field | `Flag_IncludeLymanWerner` with mini-halo and thermal paths | `ComputeTs.c`, `XRayHeatingFunctions.c`, `physics/reionization.c` |
| Baryon–dark matter streaming suppression | `Flag_IncludeStreamVel` | `src/core/cooling.c:Mcool_SV()` |
| External metal enrichment | `Flag_IncludeMetalEvo` | `src/core/metal_evo.c`; `calc_metal_bubble()` |
| Stellar magnitudes and dust attenuation | `CALC_MAGS`, external Sector source | `src/core/magnitudes.c` |
| JWST/HST observer filters | `USE_JWST`, `USE_HST` with `CALC_MAGS` | `src/core/magnitudes.c` |
| Intrinsic [O III] line | Computed on star formation updates | `src/physics/emission_lines.c` |
| Dusty [O III] line | `CALC_MAGS` plus a matching rest band | `src/core/save.c` |

The main radiation loop calls the thermal routine when the spin-temperature flag is enabled. An LW run therefore needs `Flag_IncludeSpinTemp=1` as well as `Flag_IncludeLymanWerner=1`; the threshold consumes the previously stored LW field. Runtime flags do not add fields compiled out of the binary.

## Population assignment

`Galaxy_Population=2` identifies Pop. II star formation; `3` identifies Pop. III. With mini-halos enabled, the instantaneous internal assignment is

```{math}
:label: opt-population-criterion
\text{population}=\begin{cases}
2,& Z_{\rm cold}/0.01>\texttt{ZCrit},\\
3,&\text{otherwise},
\end{cases}
\qquad Z_{\rm cold}=\frac{M_{Z,\rm cold}}{M_{\rm cold}}.
```

The divisor `0.01` is the literal normalization in the population-selection code. It differs from the `Z_SUN=0.0134` constant used for the line calculation and the `0.02` reference used for cooling/dust. Consequently `ZCrit` is not an absolute metal mass fraction. The distributed `ZCrit=0.0001` corresponds to a transition at $Z_{\rm cold}>10^{-6}$ in mass fraction.

Pop. II and III have separate SFR, stellar/gross stellar mass, new-star history, escaped source and feedback parameters. The instantaneous formation population is set by current cold-gas metallicity; existing stars retain their population histories. Pop. III remnant mass is tracked separately and is not automatically converted to the central black-hole seed or accretion reservoir.

## Pop. III initial mass functions

`initialize_PopIII()` chooses the mass bounds, ionizing yield and IMF shape. Mass $m$ below is measured in $M_\odot$ and $\phi(m)$ is the number distribution per unit formed stellar mass:

```{math}
:label: opt-popiii-imf
\phi(m)=\begin{cases}
A m^{-2.35},&\text{Salpeter cases},\\
\dfrac{A}{m}\exp\!\left[-\dfrac{\ln^2(m/m_c)}{2\sigma^2}\right],&\text{lognormal cases},
\end{cases}
\qquad \int_{m_{\min}}^{m_{\max}}m\phi(m)\,dm=1.
```

The lognormal width uses the natural logarithm; $\sigma=1$ is not one dex.

| `PopIII_IMF` | Shape | Mass interval ($M_\odot$) | $m_c$ ($M_\odot$) | Ionizing photons per stellar baryon |
|---|---|---|---:|---:|
| `1` | Salpeter | 1–500 | — | 22000 |
| `2` | Salpeter | 50–500 | — | 72000 |
| `3` | Lognormal, $\sigma=1$ | 1–500 | 10 | 47600 |
| `4` | Lognormal, $\sigma=1$ | 1–500 | 60 | 71000 |

The initializer overwrites `ReionNionPhotPerBaryIII` with the selected IMF yield. Use only the explicit selectors 1–4. For an unrecognized value, the source logs a Salpeter fallback and assigns bounds 1–100 and yield 22000, but retains the original selector. A value greater than 4 therefore enters the lognormal path with uninitialized characteristic mass and width. The logged fallback does not establish a valid alternative IMF setup.

The IMF integrals distinguish core-collapse progenitors in 8–40 $M_\odot$, pair-instability progenitors in 140–260 $M_\odot$, and direct-collapse remnants in 40–140 and above 260 $M_\odot$:

```{math}
:label: opt-popiii-fate-integrals
\begin{aligned}
N_{\rm CC}&=\int_{[8,40]\cap I}\phi(m)\,dm,&
F_{\rm CC}&=\int_{[8,40]\cap I}m\phi(m)\,dm,\\
N_{\rm PI}&=\int_{[140,260]\cap I}\phi(m)\,dm,&
F_{\rm PI}&=\int_{[140,260]\cap I}m\phi(m)\,dm,\\
F_{\rm BH,rem}&=\int_{([40,140]\cup[260,\infty))\cap I}m\phi(m)\,dm,
&&I=[m_{\min},m_{\max}].
\end{aligned}
```

$N$ is a number per solar mass formed; $F$ is a dimensionless mass fraction. The GSL integrals use a relative tolerance of 0.01.

### Stellar lifetimes and delayed yields

With $x=\log_{10}(m/M_\odot)$, the implemented [Schaerer (2002)](https://arxiv.org/abs/astro-ph/0110697) lifetime fits are

```{math}
:label: opt-popiii-lifetime
\log_{10}\!\left(\frac{t_*}{\rm yr}\right)
=a_0+a_1x+a_2x^2+a_3x^3.
```

| `PopIIIAgePrescription` | Case | $a_0$ | $a_1$ | $a_2$ | $a_3$ |
|---|---|---:|---:|---:|---:|
| `1` | Strong mass loss | 8.795 | −1.797 | 0.332 | 0 |
| `2` | No mass loss | 9.785 | −3.759 | 1.413 | −0.186 |

The inversion is linear interpolation in $(\log_{10}m,\log_{10}t_*)$ on a 0.5 $M_\odot$ mass grid and clamps lifetimes to the tabulated endpoints. The first fit was calibrated for massive stars, while the selected IMF can extend to $1M_\odot$; the source applies the polynomial across its generated IMF grid.

For a historical burst, the delayed-feedback interval selects a progenitor window $W_i$ from the inverted lifetime at the half-interval boundaries. For a burst of age $\tau_i$,

```{math}
:label: opt-popiii-delay-window
m_{\min,i}=m_*(\tau_i+\Delta t_{\rm before}/2),\qquad
m_{\max,i}=m_*(\tau_i-\Delta t_{\rm after}/2),
\qquad W_i=[m_{\min,i},m_{\max,i}]\cap[8,40]\cap I.
```

For the current burst, the upper limit is fixed to $40M_\odot$. Define $n_i=\int_{W_i}\phi\,dm$ and $f_i=\int_{W_i}m\phi\,dm$. The code's number and mass fractions are

```{math}
:label: opt-popiii-delay-fractions
q_{N,i}=\frac{n_i}{N_{\rm CC}+N_{\rm PI}},\qquad
q_{M,i}=\frac{f_i}{F_{\rm CC}+F_{\rm PI}},\qquad
Y_{k,i}=\frac{f_i}{F_{\rm CC}}\,y_k(m_{\max,i}).
```

The delayed yield coefficients use the *upper progenitor mass of the interval*, with the following piecewise values.

| Quantity $y_k$ | Upper progenitor mass ($M_\odot$) | Coefficient |
|---|---|---:|
| Recycled mass | $m_{\max}\le30$ | 0.88 |
| Recycled mass | $m_{\max}>30$ | 0.60 |
| Remnant mass | $m_{\max}\le30$ | 0.12 |
| Remnant mass | $m_{\max}>30$ | 0.40 |
| Metals | $m_{\max}\le15$ | 0.05 |
| Metals | $15<m_{\max}\le25$ | 0.09 |
| Metals | $25<m_{\max}\le30$ | 0.15 |
| Metals | $m_{\max}>30$ | 0 |

Pair-instability feedback is contemporaneous. `PISN_PopIII_Yield()` returns one for recycled mass and one half for metals when the PISN mass fraction is nonzero; the caller multiplies these values by $F_{\rm PI}$. Delayed stellar reservoir and energy updates, including remnant removal and the stochastic minimum-event treatment, are specified in [galaxy physics](galaxy-physics.md).

## Streaming velocities and LW cooling threshold

With streaming enabled, the implementation uses one rms amplitude everywhere rather than a spatial streaming-velocity realization:

```{math}
:label: opt-streaming-cooling
\sigma_{\rm bc}(z)=30\frac{1+z}{1000}\ {\rm km\ s^{-1}},\qquad
v_{\rm bc}=n\sigma_{\rm bc},\quad n\in\{0,1\},\qquad
V_{\rm cool}=\sqrt{(3.714\ {\rm km\ s^{-1}})^2+(4.015v_{\rm bc})^2}.
```

$n=1$ when `Flag_IncludeStreamVel=1`, otherwise $n=0$. Conversion to the base cooling mass uses the virial relations

```{math}
:label: opt-molecular-virial-mass
T_{\rm mol}=\min\!\left[73.8\left(\frac{V_{\rm cool}}{{\rm km\ s^{-1}}}\right)^2,10^4\right]\ {\rm K},
\qquad
M_{\rm cool,0}=10^8h^{-1}M_\odot
\left(\frac{\mu_T}{0.6}\right)^{-3/2}
\left[\frac{\Omega_m}{\Omega_m(z)}\frac{\Delta_{\rm vir}(z)}{18\pi^2}\right]^{-1/2}
\left(\frac{T_{\rm mol}}{1.98\times10^4\ {\rm K}}\right)^{3/2}
\left(\frac{1+z}{10}\right)^{-3/2}.
```

Here $\mu_T=1.22$ below the approximately $10^4$ K switch in `Tvir_to_Mvir()`, and $0.59$ above it. The molecular velocity-to-temperature routine itself caps temperature at $10^4$ K.

The local LW intensity raises the threshold:

```{math}
:label: opt-lw-mass-threshold
M_{\rm crit,MC}(\mathbf{x},z)
=M_{\rm cool,0}(z)
\left[1+6.96\{4\pi J_{\rm LW,21}(\mathbf{x},z)\}^{0.47}\right].
```

$J_{\rm LW,21}$ is measured in $10^{-21}\ {\rm erg\ s^{-1}\ Hz^{-1}\ cm^{-2}\ sr^{-1}}$. The molecular cooling branch also requires $T_{\rm vir}\ge10^3$ K and $M_{\rm vir}\ge M_{\rm crit,MC}$. Its cooling coefficients and subsequent cold-gas supply are given in [galaxy physics](galaxy-physics.md).

The thermal solver builds LW contributions from Pop. II, Pop. III and AGN sources on retarded-redshift shells, accounting for Lyman-series horizons. `JLW_box` is the total field and `JLW_boxII` the Pop. II-only field. AGN LW uses `AGNLWEfficiency` and `SpecIndexUVAGNSoft` and is enabled independently of the AGN X-ray selector. The cosmological source integrals are described in [IGM physics](igm.md).

There is a population-selection inconsistency in the current [`spectral_emissivity()`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/XRayHeatingFunctions.c): its LW integration and high-frequency continuation use the requested `flag_Pop`, but its ordinary within-segment emissivity branch tests the fixed `Pop=2` constant. Pop. III direct stellar Ly-alpha calls in those segments therefore use the Pop. II coefficients. Separate population histories alone do not remove this source-level inconsistency.

## Supernova-driven metal bubbles

External enrichment requires mini-halos and `Flag_IncludeMetalEvo=1`. `calc_metal_bubble()` evolves Sedov–Taylor-like spherical bubbles from the stored supernova energy history. For bubble energy $E$ injected at time $t_0$ and ambient hydrogen-proxy number density $n$, its physical radius is

```{math}
:label: opt-metal-bubble
R_{\rm metal}(t)=\left(\frac{E}{m_p}\right)^{1/5}n^{-1/5}(t-t_0)^{2/5}.
```

The stored `Prefactor` is $(E/m_p)^{1/5}$ divided by the internal length unit. Source energies include the appropriate supernova ejection-efficiency factor. The code constructs candidate bubbles from the available star-formation history and retains the candidate with the largest radius; galaxy mergers retain the larger existing bubble and its expansion history.

The two ambient-density estimates are

```{math}
:label: opt-metal-ambient-density
n_{\rm halo}^{\rm code}
=\frac{(M_{\rm cold}+M_{\rm hot})U_M/m_p}
{(4\pi/3)(R_{\rm vir}U_L)^3},\qquad
n_{\rm IGM}^{\rm code}
=\frac{M_{\rm gas,cell}U_M/m_p}
{[\Delta x\,U_L/(1+z)]^3},\qquad
\Delta x=\frac{L_{\rm box}}{\texttt{MetalGridDim}}.
```

$U_M$ and $U_L$ are the `UnitMass_in_g` and `UnitLength_in_cm` conversions used by this function. These expressions describe the actual source conversion, which does not insert separate factors of $h$ in the bubble calculation. Within the virial radius it uses the halo density if that density exceeds the IGM estimate; outside it uses the IGM estimate.

### Deposition, enrichment probability and infall metallicity

Galaxies are mapped by nearest-grid-point deposition onto a separate metal grid. A bubble contributes to external pollution only after $R_{\rm metal}\ge3R_{\rm vir}$. Its physical radius is converted to $R_c=(1+z)R_{\rm metal}$ for the comoving filling-factor estimate:

```{math}
:label: opt-enrichment-probability
P_{\rm enrich,cell}
=\operatorname{clip}_{[0,1]}
\left[\frac{\sum_{g\ {
m in\ cell},\ R_g\ge3R_{{\rm vir},g}}
(4\pi/3)R_{c,g}^3}{(L_{\rm box}/\texttt{MetalGridDim})^3}\right].
```

This is a sum of bubble volumes in the source cell. It is not a geometric union of resolved spheres over adjacent cells. Average and maximum bubble-radius grids are separately constructed from sources with positive radii.

The metal-mass grid sums the ejected metal masses of escaped bubbles. The gas grid starts from the cell baryon supply, removes galaxy hot/cold gas and adds eligible ejected gas. Negative results are clamped. Their ratio supplies

```{math}
:label: opt-cell-metallicity
Z_{\rm IGM,cell}=\frac{M_{Z,\rm cell}}{M_{\rm gas,cell}},\qquad
\Delta M_{Z,\rm infall}=Z_{\rm IGM,cell}\Delta M_{\rm infall}
\quad\text{for an externally enriched central galaxy}.
```

Each new galaxy draws a fixed uniform variate `GalMetal_Probability`. An unenriched central is assigned an external-enrichment flag when this variate is no greater than the cell probability, or when it has already formed stars. The subsequent formation-population decision uses its cold-gas metallicity, as above.

`NLBias()` also defines a clustering fit

```{math}
:label: opt-unused-clustering-fit
\Psi(R,M,z)=\Psi_0
\left(\frac{R}{0.01\ {\rm Mpc}}\right)^\alpha
\left(\frac{M}{10^6M_\odot}\right)^\beta
\left(\frac{z}{20}\right)^\gamma.
```

It is present as a helper but is not called by the metal-grid deposition path in this revision. The distributed clustering parameters should not be interpreted as changing the active filling-factor algorithm.

## Stellar continuum and dust

`CALC_MAGS` links an external [Sector](https://github.com/meraxes-devs/sector) source directory through `SECTOR_ROOT`. The Meraxes branch does not pin a Sector revision. `src/core/magnitudes.c` accumulates flux contributions at the selected target snapshots, separates stars younger/older than `BirthCloudLifetime`, and adds both components during mergers. Pop. III contributions use IMF-specific spectral templates and a separate flux history.

For a stellar-population luminosity kernel $\ell_\nu(\tau,Z)$ per formed stellar mass, the population-synthesis convolution is

```{math}
:label: opt-sed-convolution
L_\nu(t)=\int_0^t\dot M_*(t')\ell_\nu(t-t',Z(t'))\,dt'.
```

Meraxes evaluates this using preintegrated template responses to piecewise constant SFR intervals. `InstantSfIII=1` selects an instantaneous Pop. III response with the burst displacement `DeltaT`; `InstantSfIII=0` selects the continuous-formation template integration. The Pop. II spectra are read from `sed_library.hdf5`, and the four Pop. III filenames match the four IMF cases: `Sal500_001.hdf5`, `Sal500_050.hdf5`, `logA500_001.hdf5`, `logE500_001.hdf5`. The Sector repository identifies these Pop. III spectra with [Raiter, Schaerer & Fosbury (2010)](https://arxiv.org/abs/1008.2114).

The external formulas below are verified against [Sector revision `4824bec`](https://github.com/meraxes-devs/sector/tree/4824becc9ea8e5f7c9728b2445530ab688b386a5), inspected separately from the Meraxes revision. A chosen `SECTOR_ROOT` can supply a different version. `sector/clib/spectra.c` reads templates normalized to the flux at 10 pc. Its interval kernel is the trapezoidal integral of the raw spectrum over the stellar-age interval, with zero assumed below the first tabulated stellar age. Its instantaneous Pop. III kernel is linear age interpolation.

For a rest-frame top-hat magnitude band $[\lambda_1,\lambda_2]$, the Sector weighting of a wavelength flux $f_\lambda$ is

```{math}
:label: opt-sector-rest-filter
F_b=\frac{3.34\times10^4}{\ln(\lambda_2/\lambda_1)}
\int_{\lambda_1}^{\lambda_2}\lambda f_\lambda(\lambda)\,d\lambda,
\qquad
F_{\beta,b}=\frac{1}{\lambda_2-\lambda_1}
\int_{\lambda_1}^{\lambda_2}f_\lambda(\lambda)\,d\lambda.
```

Wavelengths are in Å; the first response is converted to the Jy convention by the numerical factor, while the beta-band response remains an average wavelength flux. For an observer transmission $T(\lambda_{\rm obs})$, the normalized kernel and pivot wavelength are

```{math}
:label: opt-sector-observer-filter
A_b=\left[\int\frac{T(\lambda_{\rm obs})}{\lambda_{\rm obs}}\,d\lambda_{\rm obs}\right]^{-1},
\qquad
\lambda_{\rm pivot,rest}
=\frac{\left[A_b\int\lambda_{\rm obs}T(\lambda_{\rm obs})\,d\lambda_{\rm obs}\right]^{1/2}}{1+z},
\qquad
W_b(\lambda_{\rm rest})
=3.34\times10^4 A_b\lambda_{\rm obs}T(\lambda_{\rm obs}),
\quad\lambda_{\rm obs}=(1+z)\lambda_{\rm rest}.
```

This on-the-fly branch produces flux/magnitude responses using rest-frame wavelengths corresponding to the observer filter. It does not add a luminosity-distance modulus in `get_output_magnitudes()`. A catalogue observer-filter entry therefore needs a separate distance/redshift conversion before comparison with observed apparent magnitudes.

The branch constructs the gas-column dust scaling used by [Qiu et al. (2019)](https://doi.org/10.1093/mnras/stz2233):

```{math}
:label: opt-dust-normalization
D=\left(\frac{Z_{\rm cold}}{0.02}\right)^{p_Z}
M_{\rm cold}^{\rm int}
\left(10^3R_{\rm disk}^{\rm int}\right)^{-2}
\exp(a_z z),\qquad
\tau_{\rm UV,ISM}=\tau_{\rm ISM,0}D,\qquad
\tau_{\rm UV,BC}=\tau_{\rm BC,0}D.
```

$M^{\rm int}$ and $R^{\rm int}$ are internal mass and length values. The normalization is tied to those units, rather than an arbitrary physical $M/R^2$ substitution. `DustMetallicityScale`, `DustAZ`, `DustTauUVISM` and `DustTauUVBC` supply $p_Z$, $a_z$ and the two amplitudes. Their distributed defaults are $1.2$, $-0.35$, $13.5$ and $381.3$; the two spectral slopes `DustNISM` and `DustNBC` are both $-1.6$, and the birth-cloud lifetime is $10^7$ yr.

The called `dust_absorption_approx()` applies the Charlot–Fall-style attenuation at each band's rest-frame central/pivot wavelength:

```{math}
:label: opt-sector-dust-attenuation
\tau_{\rm ISM}(\lambda)=\tau_{\rm UV,ISM}
\left(\frac{\lambda}{1600\ {\rm \mathring A}}\right)^{n_{\rm ISM}},\qquad
\tau_{\rm BC}(\lambda)=\tau_{\rm UV,BC}
\left(\frac{\lambda}{1600\ {\rm \mathring A}}\right)^{n_{\rm BC}},\qquad
F_b^{\rm dusty}=e^{-\tau_{\rm ISM}(\lambda_b)}
\left[e^{-\tau_{\rm BC}(\lambda_b)}F_b^{\rm young}+F_b^{\rm old}\right].
```

This is band-centre attenuation rather than re-integrating the attenuated spectrum across a wide filter. Birth clouds attenuate the young component; the ISM attenuates both.

The catalogue conversion for a band response $F_b^{\rm code}$ is

```{math}
:label: opt-ab-magnitude
M_b=-2.5\log_{10}F_b^{\rm code}+8.9
-2.5\log_{10}\!\left[
\frac{U_M}{U_t}\frac{{\rm seconds\ per\ year}}{M_\odot}\right].
```

The external library handles filter normalization and observer-band redshifting. `TargetSnaps` determines the template epochs and must be consistent with the compiled `MAGS_N_SNAPS`; the number of rest/beta/JWST/HST bands must equal `MAGS_N_BANDS`. Nontarget snapshots receive magnitude sentinel `999.999`. `MagsIII` is the Pop. III-only contribution, while `Mags` includes both populations. Meraxes places the Pop. III contribution in the older/outside-birth-cloud component of the total flux before applying the dust model.

## [O III] 5008 Å line model

The present source evaluates the line during star formation updates and initializes its collision coefficients at $T=10^4$ K. It implements a specific disk/bubble approximation; it is not a general photoionization-code calculation or a full nebular spectrum.

### Collision coefficients

Let $u=T/(10^4\ {\rm K})$. The implemented collision strengths and upward excitation rates are

```{math}
:label: opt-oiii-collision
\begin{aligned}
\Omega_{30}&=0.243\,u^{0.120+0.031\ln u},\qquad
\Omega_{40}=0.0321\,u^{0.118+0.057\ln u},\\
\beta_q&=10^6\sqrt{\frac{2\pi\hbar^4}{k_Bm_e^3}},\\
k_{03}&=\beta_q T^{-1/2}\Omega_{30}e^{-29169/T},\qquad
k_{04}=\beta_q T^{-1/2}\Omega_{40}e^{-61207/T},\\
k_{\rm exc}&=k_{03}+k_{04}\frac{A_{43}}{A_{43}+A_{41}},\qquad
b_{32}=\frac{A_{32}}{A_{32}+A_{31}}.
\end{aligned}
```

$\hbar,k_B,m_e$ in $\beta_q$ use SI constants and the $10^6$ factor converts to the cgs collision-rate convention. The transition values are $A_{31}=4.57\times10^{-6}$, $A_{32}=3.52\times10^{-5}$, $A_{41}=0.215$ and $A_{43}=1.7\ {\rm s^{-1}}$.

### Disk, turbulent support and source bubbles

Write $M_d=M_*+M_{\rm cold}$, $m_d=M_d/M_{\rm vir}$ and $c_s^2=10^{12}\ {\rm cm^2\ s^{-2}}$. After conversion to the physical cgs quantities used in this routine, the star-forming bubble-radius proxy is

```{math}
:label: opt-oiii-bubble-radius
r_b^3=(8\times10^{-5}\ {\rm Mpc})^3
\left(\frac{\lambda}{0.05}\right)^4
\left(\frac{m_d}{0.17}\right)^{-2}
\left(\frac{M_{\rm vir}^{\rm int}\,10^2}{h}\right)^{-2/3}
\left(\frac{1+z}{10}\right)^{-4}.
```

$\lambda$ is the stored halo spin and $R_d$ the disk scale length. The initial density expression and the two support terms are

```{math}
:label: opt-oiii-disk-support
\begin{aligned}
\rho_0&=\frac{GM_{\rm cold}M_d}{58.7528\pi c_s^2R_d^4},\\
\dot\Sigma_{\rm SN}&=\frac{0.156\dot M_*}{12.26M_\odot\pi R_d^2},\qquad
s_{\rm SN}=\frac{(2\dot\Sigma_{\rm SN}\,0.03E_{\rm SN}/\rho_0)^{2/3}}{c_s^2},\\
\delta^{-1}&=\frac{M_{\rm vir}(R_d/R_{\rm vir})^3+M_{\rm cold}+M_*}{M_{\rm cold}},\\
Q^2&=0.98\delta^{-2}\frac{c_s^2}{(1.4V_{\max})^2},\qquad
s_{\rm acc}=\frac{(0.6G\dot M_{\rm cool}Q^2/2.94)^{2/3}}{c_s^2},\\
\rho_{\rm code}&=\frac{\rho_0}{1+s_{\rm SN}+s_{\rm acc}},\qquad
N_b=\frac{3M_d}{4\pi\rho_{\rm code}r_b^3},\qquad
\dot N_{\gamma,b}=\frac{4000\dot M_*}{m_pN_b}.
\end{aligned}
```

Here $E_{\rm SN}=10^{51}$ erg and $\dot M_{\rm cool}=M_{\rm cool}/\Delta t$. The line model uses the fixed yield 4000 even when the global ionization yield parameter is overridden. It uses the Pop. II `Sfr` field.

The code inserts its density proxy into

```{math}
:label: opt-oiii-stromgren
r_S^2=\left[\frac{3\dot N_{\gamma,b}}{4\pi\alpha_B\rho_{\rm code}^2}\right]^{2/3},
\qquad
\texttt{ionization\_param}\ \mathrel{+}=
\frac{1.5874\dot N_{\gamma,b}}{4\pi r_S^2\rho_{\rm code}},
\qquad \alpha_B=2.6\times10^{-13}\ {\rm cm^3\ s^{-1}}.
```

These are the literal implementation formulas. $\rho_0$ has mass-density units, while the Strömgren expression normally requires hydrogen number density; this routine does not divide by $m_p$ at that substitution. It also omits the $1/c$ factor required for a dimensionless ionization parameter. Accordingly the stored `ionization_param` should not be treated as a calibrated dimensionless $U$ without correcting and validating these conversions.

### Luminosity and dust

The line luminosity is

```{math}
:label: opt-oiii-luminosity
L_{5008}=\left[\frac{10^{8.69-12}}{0.0134}Z_{\rm cold}\right]
k_{\rm exc}b_{32}
\frac{\dot N_{\gamma,b}N_b}{\alpha_B}
h_P\nu_{32}\,f_{\rm OIII},
\qquad \nu_{32}=\frac{c}{5008\ {\rm \mathring A}},\quad f_{\rm OIII}=0.8.
```

`LOIII` stores $L_{5008}/(10^{40}\ {\rm erg\ s^{-1}})$. Each star formation call adds a nonnegative finite contribution and mergers add the inherited luminosities. If required input reservoirs, sizes, halo velocity or time interval are invalid, the line routine returns without adding a contribution.

With a matching rest-frame continuum band, dust attenuation is inferred from the synthetic magnitude difference:

```{math}
:label: opt-oiii-dust
L_{5008}^{\rm dusty}=L_{5008}\,10^{0.4(M_b-M_b^{\rm dusty})}.
```

The selected rest band must contain 5008 Å. Without a suitable continuum band, the dusty value remains equal to the intrinsic value. This revision does not write an equivalent-width catalogue field. Details of the line luminosity-function products are given in [outputs](outputs.md).

## Source map

| Topic | Source entry points |
|---|---|
| IMF selection, normalization and stellar fates | [`src/core/PopIII.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/PopIII.c): `initialize_PopIII()`, `getIMF()`, fate-integral routines |
| Lifetime and burst-window interpolation | [`src/core/PopIII.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/PopIII.c): `get_StellarAge()`, `interp_mass()`, `CCSN_PopIII_Number()` |
| Streaming cooling mass | [`src/core/cooling.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/cooling.c): `Mcool_SV()` |
| LW threshold | [`src/physics/reionization.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/reionization.c): `calculate_Mvir_crit_MC()` |
| Population-dependent stellar emissivity | [`src/core/XRayHeatingFunctions.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/XRayHeatingFunctions.c): `spectral_emissivity()` |
| Internal/external formation population | [`src/physics/evolve.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/evolve.c): `evolve_galaxies()` |
| Metal bubble growth | [`src/physics/supernova_feedback.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/supernova_feedback.c): `calc_metal_bubble()` |
| Metal deposition and galaxy sampling | [`src/core/metal_evo.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/metal_evo.c): `construct_metal_grids()`, `assign_probability_to_galaxies()` |
| Template accumulation and dust arguments | [`src/core/magnitudes.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/magnitudes.c): `add_luminosities()`, `get_output_magnitudes()` |
| [O III] coefficients and line | [`src/physics/emission_lines.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/emission_lines.c): `set_OIII_coeffs()`, `compute_LOIII()` |
| Dusty line and distribution products | [`src/core/save.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/save.c): `prepare_galaxy_for_output()`, `write_snapshot()` |
