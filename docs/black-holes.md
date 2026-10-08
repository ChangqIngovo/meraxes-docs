# Black holes and active galactic nuclei

Meraxes follows one central black hole per galaxy, merger-fed cold accretion, hot-gas accretion and the corresponding energy and photon budgets. The original development is described by [Qin et al. (2017)](https://arxiv.org/abs/1703.04895). This page specifies the implementation in the documented `forests` revision; later luminosity and obscuration prescriptions are identified separately.

The main implementation is [`src/physics/blackhole_feedback.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/blackhole_feedback.c), with seeding and snapshot resets in `src/core/galaxies.c`, mergers in `src/physics/mergers.c` and escape fractions and deposition in `src/core/reionization.c`. See [galaxy physics](galaxy-physics.md) for reservoir evolution and [IGM physics](igm.md) for how AGN radiation enters the radiation fields.

## State, units and activation

| State or control | Meaning |
|---|---|
| `BlackHoleMass` | Central black-hole mass, in internal mass units |
| `BlackHoleAccretingColdMass` | Cold gas transferred to an unresolved accretion reservoir and still awaiting accretion |
| `BlackHoleAccretedColdMass`, `BlackHoleAccretedHotMass` | Gas accreted during the current output interval |
| `EffectiveBHM` | Cumulative escaped ionizing budget expressed as an equivalent stellar source mass |
| `EffectiveBHAR` | Current equivalent source rate, with duty-cycle or response-time weighting |
| `QuasarLuv`, `QuasarLX` | Intrinsic 1450 Å and hard X-ray luminosities in units of $10^{10}L_\odot$ |
| `BHXrayEmissivity_soft`, `BHXrayEmissivity_hard` | Transmitted soft/hard X-ray luminosities, stored internally in the same luminosity units |
| `DutyCycleAGN` | Accretion duration divided by the effective interval, limited to $[0,1]$ |
| `BHAccretionOnTime` | Fractional accretion start time; negative when no episode is active |
| `Flag_BHFeedback` | Enables radio-mode heating and merger-driven provisioning of new cold accretion reservoirs |
| `Flag_IncludeAGNXray` | `0`: none; `1`: soft and hard; `2`: hard only; `3`: soft only |
| `BlackHoleMassLimitReion` | Minimum internal `BlackHoleMass` included in the ionizing, soft/hard X-ray and LW AGN source grids |

Seeding and black-hole addition in galaxy mergers occur independently of `Flag_BHFeedback`. An existing cold reservoir is accreted whenever it is positive; the evolution routine does not recheck that flag. `Flag_IncludeAGNXray` selects radiation entering the thermal solver, rather than whether black-hole growth occurs.

## Seeding and mergers

A newly allocated galaxy receives

```{math}
:label: bh-seed
M_{\rm BH}=M_{\rm seed},\qquad
M_{\rm seed}=\texttt{BlackHoleSeed}.
```

The distributed default is $10^{-7}$ internal mass units, equivalent to $10^3h^{-1}M_\odot$ with the standard $10^{10}h^{-1}M_\odot$ mass unit. This is a fixed seed, rather than a halo-threshold or resolved Pop. III remnant seeding algorithm. The optional Pop. III `Remnant_Mass` reservoir is separate from `BlackHoleMass`.

Galaxy mergers add the black-hole masses, unaccreted cold reservoirs, accumulated source budgets and current luminosities. The surviving galaxy adopts the duty cycle and response time of the more massive pre-merger black hole.

## Hot accretion and radio-mode heating

For a central galaxy with hot gas and nonzero cooling, the routine uses the cooling-dependent Bondi–Hoyle form

```{math}
:label: bh-hot-accretion
\Delta M_{\rm hot}^{\rm trial}
=\kappa_{\rm R}\,G\,C_{\rm B}\,X\,M_{\rm BH}\,\Delta t,
\qquad C_{\rm B}=3.4754,
\qquad X=\frac{m_p k_B T_{\rm vir}}{\Lambda(T_{\rm vir},Z)}.
```

Here $\kappa_{\rm R}=\texttt{RadioModeEff}$, $X$ is converted to the internal density–time units by the cooling routine, and $\Delta t$ is the galaxy evolution interval. The literal hot-mode cap in this revision is

```{math}
:label: bh-hot-cap
\Delta M_{\rm hot}
=\min\!\left[
\Delta M_{\rm hot}^{\rm trial},\,
M_{\rm BH}\exp\!\left(\frac{\lambda_{\rm Edd}\Delta t}{\eta t_E}\right),\,
M_{\rm hot}\right],
\qquad \eta=0.06,\quad t_E=450.514890\ {\rm Myr}.
```

$\lambda_{\rm Edd}=\texttt{EddingtonRatio}$. The hot cap contains `exp`, whereas cold accretion below uses `expm1`; they are different expressions in the current source. The hot expression should therefore not be interpreted as the usual exponential *mass increment*.

The energy available to offset cooling corresponds to

```{math}
:label: bh-radio-heating
\Delta M_{\rm heat,R}
=\frac{2\eta c^2}{V_{\rm vir}^2}\Delta M_{\rm hot}.
```

If this exceeds the cooling mass, both the heating and accretion are reduced by the same factor so that $\Delta M_{\rm heat,R}=\Delta M_{\rm cool}$. The hot gas and its proportional metal content are removed, while the black hole gains $(1-\eta)\Delta M_{\rm hot}$. The cooling mass is reduced by the heated mass. Radio-mode radiation is assigned entirely to heating the cooling flow: this routine adds no ionizing or X-ray source emissivity.

For a nonghost central galaxy, $V_{\rm vir}$ is the FOF-group velocity; otherwise its own stored virial velocity is used.

## Merger-fed cold reservoir

Let $\mu$ be the smaller-to-larger baryonic merger ratio used by the merger routine. Cold gas is transferred onto the accretion reservoir according to

```{math}
:label: bh-merger-reservoir
\Delta M_{\rm disk}
=\min\!\left[
M_{\rm cold},\,
\frac{f_{\rm BH}\,\mu\,(1+z)^{p_{\rm Q}}}
{1+(280\ {\rm km\ s^{-1}}/V_{\rm vir})^2}
M_{\rm cold}\right].
```

$f_{\rm BH}=\texttt{BlackHoleGrowthRate}$ and $p_{\rm Q}=\texttt{quasar\_mode\_scaling}$. The corresponding cold metals are removed at the current cold-gas metallicity. This reservoir is provisioned at the end of galaxy evolution and accreted in subsequent snapshots. It is not an instantaneous black-hole mass increase.

## Eddington-limited cold accretion and timing

Cold accretion uses the interval between consecutive snapshot lookback times, including for ghost galaxies:

```{math}
:label: bh-cold-interval
\Delta t_{\rm snap}=t_{\rm lookback}(i-1)-t_{\rm lookback}(i),
\qquad
\Delta t_{\rm eff}=
\begin{cases}
\Delta t_{\rm snap},&\texttt{Flag\_BHARExponentialCut}=0,\\
(1-u)\Delta t_{\rm snap},&\text{first interval of an episode with the flag}=1,\\
\Delta t_{\rm snap},&\text{continuing episode with the flag}=1.
\end{cases}
```

The first-episode $u$ is drawn uniformly in $[0,1)$. No elapsed time means no accretion. The gas increment and subsequent black-hole update are

```{math}
:label: bh-cold-accretion
\Delta M_{\rm acc}
=\min\!\left[
M_{\rm disk},\,
M_{\rm BH}\left\{
\exp\!\left(\frac{\lambda_{\rm Edd}\Delta t_{\rm eff}}{\eta t_E}\right)-1
\right\}\right],
\qquad
M_{\rm BH}\longleftarrow M_{\rm BH}+(1-\eta)\Delta M_{\rm acc}.
```

The source calculates an episode duration and midpoint luminosity from the pre-accretion black-hole mass:

```{math}
:label: bh-duration-lbol
t_{\rm acc}=\frac{\eta t_E}{\lambda_{\rm Edd}}
\ln\!\left(1+\frac{\Delta M_{\rm acc}}{M_{\rm BH}}\right),
\qquad
L_{\rm bol}=\frac{\lambda_{\rm Edd}c^2}{t_E}
\sqrt{M_{\rm BH}(M_{\rm BH}+\Delta M_{\rm acc})},
\qquad
f_{\rm duty}=\operatorname{clip}_{[0,1]}
\left(\frac{t_{\rm acc}}{\Delta t_{\rm eff}}\right).
```

These expressions reproduce the code convention: the exponential rate and luminosity midpoint do not replace $\Delta M_{\rm acc}$ by the retained increment $(1-\eta)\Delta M_{\rm acc}$. The residual disk is reduced by the full gas increment. Once it is exhausted, the on-time state resets to a negative value.

## Bolometric corrections and ionizing photons

The implemented corrections are labelled [Shen et al. (2020)](https://arxiv.org/abs/2001.02696). For $\ell=L_{\rm bol}/(10^{10}L_\odot)$,

```{math}
:label: bh-bolometric-corrections
\begin{aligned}
k_{1450}(\ell)&=1.862\ell^{-0.361}+4.870\ell^{-0.0063},\\
k_{\rm hard}(\ell)&=4.073\ell^{-0.026}+12.60\ell^{0.278},\\
k_{\rm soft}(\ell)&=5.712\ell^{-0.026}+17.67\ell^{0.278},\\
L_{1450}&=L_{\rm bol}/k_{1450},\qquad
L_{\rm X,hard}=L_{\rm bol}/k_{\rm hard},\qquad
L_{\rm X,soft}=L_{\rm bol}/k_{\rm soft}.
\end{aligned}
```

$L_{1450}$ denotes $\nu L_\nu$ at 1450 Å. The spectral indices `SpecIndexUVAGNSoft` and `SpecIndexUVAGNHard` describe $L_\nu\propto\nu^{-\alpha}$ longward and shortward of 912 Å; the distributed values are based on [Lusso et al. (2015)](https://arxiv.org/abs/1503.02075). For positive ionizing spectral index, integration of the adopted continuum gives

```{math}
:label: bh-ionizing-rate
L_\nu(912)=\frac{L_{1450}}{\nu_{1450}}
\left(\frac{\nu_{912}}{\nu_{1450}}\right)^{-\alpha_{\rm UV,soft}},
\qquad
\dot N_{\gamma,\rm int}
=\frac{L_\nu(912)}{h_P\alpha_{\rm UV,hard}}.
```

$h_P$ is Planck's constant. Two separate geometric/escape factors multiply this rate:

```{math}
:label: bh-uv-escape
f_{\rm open}=1-\cos(\theta_{\rm Q}/2),
\qquad
f_{\rm esc,BH}=\operatorname{clip}_{[0,1]}
\left[f_{\rm BH,esc,0}
\left(\frac{1+z}{6}\right)^{p_{\rm BH,esc}}\right],
\qquad
\Delta N_{\gamma,\rm esc}
=f_{\rm open}f_{\rm esc,BH}\dot N_{\gamma,\rm int}t_{\rm acc}.
```

$\theta_{\rm Q}=\texttt{quasar\_open\_angle}$ is supplied in degrees and converted internally to radians; the distributed $80^\circ$ gives $f_{\rm open}\simeq0.234$. `quasar_fobs` stores this *open/observable fraction*, despite the wording of the startup log. $f_{\rm BH,esc,0}$ and $p_{\rm BH,esc}$ are `EscapeFracBHNorm` and `EscapeFracBHScaling`.

To reuse the stellar-source ionization machinery, the photon budget is expressed as an equivalent stellar mass using the Pop. II ionizing yield $N_{\gamma,*}=\texttt{ReionNionPhotPerBary}$:

```{math}
:label: bh-equivalent-sources
\Delta M_{\rm BH,eff}
=\frac{m_p\Delta N_{\gamma,\rm esc}}{N_{\gamma,*}},
\qquad
M_{\rm BH,eff}\longleftarrow M_{\rm BH,eff}+\Delta M_{\rm BH,eff},
\qquad
\dot M_{\rm BH,eff}^{\rm on}=\frac{\Delta M_{\rm BH,eff}}{t_{\rm acc}}.
```

The first expression defines the physical equivalent mass. The literal numeric increment stored by the source is

```{math}
:label: bh-equivalent-stored-increment
\Delta\texttt{EffectiveBHM}
=B\,(8.40925088\times10^{-8})\,
\frac{f_{\rm esc,BH}}{N_{\gamma,*}},
\qquad B=\frac{f_{\rm open}\dot N_{\gamma,\rm int}t_{\rm acc}}{10^{60}}.
```

Here $B$ is the pre-escape photon count returned in the variable `BHemissivity`. The numeric constant converts $10^{60}$ proton masses to units of $10^{10}M_\odot$; this update contains no additional factor of $h$. The output writer labels `EffectiveBHM` with units `1e10 solMass` and Hubble conversion `v/h`. Retain this distinction between the literal accumulator and the writer's declared conversion when interpreting the equivalent mass; inserting an extra $h$ into the increment would change the documented implementation.

`EffectiveBHM` stores the cumulative equivalent source mass, not the physical black-hole mass. With duty-cycle weighting, `EffectiveBHAR` receives $f_{\rm duty}\dot M_{\rm BH,eff}^{\rm on}$. With the exponential option, it receives

```{math}
:label: bh-response-weight
\dot M_{\rm BH,eff}^{\rm response}
=\dot M_{\rm BH,eff}^{\rm on}
\exp\!\left[-\frac{(1-f_{\rm duty})\Delta t_{\rm eff}}{t_{\rm resp}}\right]
\quad(t_{\rm resp}>0).
```

The exponential is applied only when both off-time and response time are positive; otherwise the on-state rate is retained. Each snapshot resets the galaxy `t_resp` to `1e30`. It is replaced by the previous IGM grid's response time only when `Flag_PatchyReion`, `ReionUVBFlag` and `Flag_IncludeRecombinations` are all enabled, through `assign_Mvir_crit_to_galaxies(...,3)`. The accretion routine converts this sampled time to internal units as $t_{\rm resp}^{\rm int}=t_{\rm resp}^{\rm stored}h/\texttt{UnitTime\_in\_Megayears}$. If the sampling path is inactive, the very large reset value makes response damping negligible. The cumulative ionizing budget is updated before this rate weighting.

The intrinsic UV absolute magnitude written to the catalogue is

```{math}
:label: bh-quasar-magnitude
M_{1450}=-19.07395-2.5\log_{10}
\left[\frac{L_{1450}}{10^{10}L_\odot}\right].
```

Inactive sources receive the sentinel `999.9`. The quasar luminosity function weights sources by $f_{\rm duty}f_{\rm open}$; the magnitude itself is intrinsic. See [outputs](outputs.md).

## X-ray obscuration

The source implements a luminosity/redshift dependent column distribution of the [Ueda et al. (2014)](https://arxiv.org/abs/1402.1836) form, followed by a random column-bin draw per accretion update. For intrinsic hard luminosity $\ell_X=\log_{10}[L_{\rm X,hard}/({\rm erg\ s^{-1}})]$,

```{math}
:label: bh-obscured-fraction
\psi=\operatorname{clip}_{[0.20,0.84]}
\left[0.43\{1+\min(z,2)\}^{0.48}-0.24(\ell_X-43.75)\right],
\qquad \epsilon=1.7,\qquad f_{\rm CTK}=1.
```

The five raw probability densities are

```{math}
:label: bh-column-distribution
\begin{aligned}
g_0&=\begin{cases}
1-\dfrac{2+\epsilon}{1+\epsilon}\psi,&\psi<\dfrac{1+\epsilon}{3+\epsilon},\\
\dfrac23-\dfrac{3+2\epsilon}{3+3\epsilon}\psi,&\text{otherwise},
\end{cases}\\
g_1&=\begin{cases}
\dfrac{\psi}{1+\epsilon},&\psi<\dfrac{1+\epsilon}{3+\epsilon},\\
\dfrac13-\dfrac{\epsilon}{3+3\epsilon}\psi,&\text{otherwise},
\end{cases}\\
g_2&=\frac{\psi}{1+\epsilon},\qquad
g_3=\frac{\epsilon\psi}{1+\epsilon},\qquad
g_4=\frac{f_{\rm CTK}\psi}{2},\\
A&=g_0+g_1+g_2+g_3+2g_4,\qquad
P_j=g_j/A\ (j<4),\qquad P_4=2g_4/A.
\end{aligned}
```

| `NHbin` | $\log_{10}(N_H/{\rm cm^{-2}})$ interval | Column midpoint used for transmission |
|---|---|---|
| `0` | $20$–$21$ | $20.5$ |
| `1` | $21$–$22$ | $21.5$ |
| `2` | $22$–$23$ | $22.5$ |
| `3` | $23$–$24$ | $23.5$ |
| `4` | $24$–$26$ | $25.0$ |

The last bin is two dex wide; the sampling probability includes that factor of two. The exposed `get_nh_fracs()` routine returns the normalized densities $g_j/A$, rather than a five-element vector whose unweighted sum is one.

For a selected bin, precomputed band transmissions are obtained from

```{math}
:label: bh-xray-transmission
T_b(N_H)=
\frac{\int_{E_{b,\min}}^{E_{b,\max}}
E^{-\gamma_b}\exp[-N_H\sigma_{\rm pe}(E)]\,C_{\rm T}(N_H)\,dE}
{\int_{E_{b,\min}}^{E_{b,\max}} E^{-\gamma_b}\,dE},
\qquad
C_{\rm T}=\begin{cases}
\exp[-1.21\sigma_TN_H],&\log_{10}N_H\ge24,\\
1,&\text{otherwise},
\end{cases}
```

where $\sigma_T=6.6524\times10^{-25}\ {\rm cm^2}$. The implementation uses 200 equally spaced midpoint samples in energy. $\gamma_b$ is taken directly from `SpecIndexXrayAGNSoft` or `SpecIndexXrayAGNHard`; the integral above describes the code's weighting without an additional energy factor. The transmitted source luminosity is $L_{\rm X,b}^{\rm esc}=T_b L_{\rm X,b}$.

The piecewise [Morrison & McCammon (1983)](https://ntrs.nasa.gov/citations/19830056692) fit is

```{math}
:label: bh-photoelectric-cross-section
\sigma_{\rm pe}(E)
=10^{-24}(C_0+C_1E+C_2E^2)E^{-3}\ {\rm cm^2},\qquad E\text{ in keV}.
```

| $E$ interval (keV) | $C_0$ | $C_1$ | $C_2$ |
|---|---:|---:|---:|
| 0.030–0.100 | 17.3 | 608.1 | −2150.0 |
| 0.100–0.284 | 34.6 | 267.9 | −476.1 |
| 0.284–0.400 | 78.1 | 18.8 | 4.3 |
| 0.400–0.532 | 71.4 | 66.8 | −51.4 |
| 0.532–0.707 | 95.5 | 145.8 | −61.1 |
| 0.707–0.867 | 308.9 | −380.6 | 294.0 |
| 0.867–1.303 | 120.6 | 169.3 | −47.7 |
| 1.303–1.840 | 141.3 | 146.8 | −31.5 |
| 1.840–2.471 | 202.7 | 104.7 | −17.0 |
| 2.471–3.210 | 342.7 | 18.7 | 0.0 |
| 3.210–4.038 | 352.2 | 18.7 | 0.0 |
| 4.038–7.111 | 433.9 | −2.4 | 0.75 |
| 7.111–8.331 | 629.0 | 30.9 | 0.0 |
| 8.331–10.000 | 701.2 | 25.2 | 0.0 |

The routine returns zero cross-section below 0.03 keV and at or above the upper table boundary. This fit describes host absorption, distinct from the cosmological IGM attenuation calculated by the thermal solver.

Unlike the UV ionizing-rate accumulator, the per-galaxy X-ray luminosities stored here are not multiplied by the duty cycle or the opening-angle factor. Histogram and thermal-grid routines have their own selection and weighting; consult [IGM physics](igm.md) and [outputs](outputs.md).

## Quasar-mode mechanical feedback

After cold accretion, the requested reheated mass is

```{math}
:label: bh-quasar-heating
\Delta M_{\rm heat,Q}
=\epsilon_{\rm Q}\frac{2\eta c^2}{V_{\rm vir}^2}\Delta M_{\rm acc},
\qquad \epsilon_{\rm Q}=\texttt{QuasarModeEff}.
```

If this is smaller than the galaxy cold-gas mass, the requested mass and corresponding cold metals move to the FOF central's hot reservoir. In the other branch, the code clears the entire cold reservoir, subtracts the full requested heated mass from the central hot reservoir and adds that requested mass to its ejected reservoir. Negative reservoirs are then clamped to zero. This second branch is the literal implemented update and does not implement a sequential, energy-limited transfer of the remaining mass after cold reheating.

## Distributed defaults

These values come from `input/params/defaults.par`; a run's parameter file may override them.

| Parameter | Default | Role |
|---|---:|---|
| `Flag_BHFeedback` | `1` | Hot heating and new merger-fed reservoirs |
| `RadioModeEff` | `0.3` | Hot accretion normalization |
| `QuasarModeEff` | `0.0005` | Cold-mode mechanical coupling |
| `BlackHoleGrowthRate` | `0.05` | Merger-fed cold reservoir efficiency |
| `EddingtonRatio` | `1.0` | Accretion/luminosity normalization |
| `BlackHoleSeed` | `1e-7` | Seed mass in internal units |
| `BlackHoleMassLimitReion` | `-1` | No positive mass threshold by default |
| `quasar_mode_scaling` | `0.0` | Reservoir redshift exponent |
| `quasar_open_angle` | `80.0` | Full opening angle in degrees |
| `EscapeFracBHNorm` | `1` | Ionizing escape normalization |
| `EscapeFracBHScaling` | `0` | Ionizing escape redshift exponent |
| `Flag_BHARExponentialCut` | `0` | Duty-cycle weighting by default |
| `Flag_IncludeAGNXray` | `0` | AGN thermal X-ray sources disabled by default |
| `SpecIndexUVAGNSoft` | `0.61` | Continuum longward of 912 Å |
| `SpecIndexUVAGNHard` | `1.70` | Ionizing continuum shortward of 912 Å |
| `SpecIndexXrayAGNSoft` | `2.2` | Soft X-ray spectral weighting |
| `SpecIndexXrayAGNHard` | `1.7` | Hard X-ray spectral weighting |
| `NuXrayThreshold` | `500` | Escaping low-energy threshold, eV |
| `NuXraySoftCut` | `2000` | Soft/hard dividing energy, eV |
| `NuXrayMax` | `10000` | Maximum integration energy, eV |
| `AGNLWEfficiency` | `1.0` | Additional AGN LW amplitude factor |

AGN LW radiation uses the UV source grid and requires the LW and spin-temperature path. Its activation is independent of `Flag_IncludeAGNXray`. Stellar scatter and source recalibration are documented on the separate [stochasticity](stochasticity.md) page.
