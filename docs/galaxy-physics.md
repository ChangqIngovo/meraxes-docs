(galaxy-physics)=
# Galaxy formation and evolution

Meraxes evolves the baryonic contents of galaxies along halo merger trees. The halo catalogue supplies positions, velocities, angular momenta and masses; the semi-analytic model follows gas accretion, cooling, star formation, stellar feedback and galaxy mergers. These processes determine the stellar and black-hole sources used by the [IGM calculation](igm.md).

This page describes the implementation at commit [`90d8474`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95). The original framework is presented by [Mutch et al. (2016)](https://arxiv.org/abs/1512.00562). Subsequent work examined high-redshift gas accretion and cooling ([Qin et al., DRAGONS XIV](https://arxiv.org/abs/1802.03879)), stellar evolution and feedback ([Qin et al., DRAGONS XV](https://arxiv.org/abs/1808.03433)), and joint galaxy/dust calibration ([Qiu et al. 2019](https://arxiv.org/abs/1905.02759)). Equations below follow the current source, including selector-dependent alternatives.

```{figure} _static/galaxy-physics.svg
:alt: Baryonic reservoirs and the physical processes connecting them
:name: fig-galaxy-physics

Gas cycling and stellar growth. Infall, cooling, reheating, ejection and reincorporation transfer mass between reservoirs; mergers combine galaxy properties and their stored histories.
```

## State variables and galaxy types

Each galaxy stores cold gas, hot gas, ejected gas, surviving stellar mass, black-hole mass and the corresponding metal reservoirs. `GrossStellarMass` records total formed stellar mass before recycling; it differs from `StellarMass`. The optional mini-halo extension separates Population II and III components and adds stellar-remnant mass.

| State | Physical interpretation | Main source fields |
|---|---|---|
| Cold gas | Gas available to form stars and feed cold-mode black-hole growth | `ColdGas`, `MetalsColdGas` |
| Hot gas | Halo gas that can cool onto the central galaxy | `HotGas`, `MetalsHotGas` |
| Ejected gas | Gas outside the cooling reservoir, available for later reincorporation | `EjectedGas`, `MetalsEjectedGas` |
| Surviving stars | Formed stars after recycled mass is removed | `StellarMass`, `MetalsStellarMass` |
| Formed stars | Cumulative mass converted into stars, including inherited progenitor contributions | `GrossStellarMass` |
| Stellar history | Formed mass and initial metal mass in recent snapshot bins | `NewStars[]`, `NewMetals[]` |
| Black holes | Central black-hole mass and queued/accreted gas | See [black holes](black-holes.md) |

The integer `Type` describes membership of a resolved halo, rather than a stellar population:

| `Type` | Meaning | Evolution |
|---|---|---|
| `0` | Central galaxy in a friends-of-friends (FOF) group | Receives group infall, cooling and reincorporation; also forms stars and undergoes feedback |
| `1` | Galaxy associated with a resolved satellite subhalo | Forms stars and undergoes feedback; its hot/ejected reservoirs are transferred to the FOF central |
| `2` | Orphan galaxy whose subhalo has merged/disappeared into another identified halo | Continues baryonic evolution while a merger clock counts down |
| `3` | Galaxy already merged into its target | Excluded from active galaxy evolution and followed only to resolve merger-target chains |

`ghost_flag` is a separate state for a galaxy whose halo is temporarily absent from the trees. It is not a fifth `Type`. A ghost retains its baryonic history while delayed stellar feedback and queued black-hole accretion continue. In-situ star formation resumes when its halo is reidentified.

Source: [`galaxies.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/galaxies.c), [`evolve.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/evolve.c).

## Units and halo quantities

The physical routines use the unit scales configured for the simulation. Write them as $U_M$, $U_L$, $U_V$, with $U_T=U_L/U_V$. The conventional Meraxes interpretation is masses in $10^{10}h^{-1}M_\odot$, halo radii in physical $h^{-1}\mathrm{Mpc}$, and velocities in $\mathrm{km\,s^{-1}}$. Catalogue positions and `BoxSize` are comoving. The [input reference](inputs.md) and [output metadata](outputs.md) specify the conversion for each property.

```{math}
:label: gal-unit-scales
U_T=\frac{U_L}{U_V},\qquad
U_\rho=\frac{U_M}{U_L^3},\qquad
U_E=U_M U_V^2,\qquad
G_{\rm int}=G_{\rm cgs}\frac{U_M U_T^2}{U_L^3}.
```

The cosmology helpers define

```{math}
:label: gal-expansion
E(z)=\left[\Omega_{m,0}(1+z)^3+\Omega_{k,0}(1+z)^2+\Omega_{\Lambda,0}\right]^{1/2},
\qquad H(z)=H_0E(z),\qquad
\Omega_m(z)=\frac{\Omega_{m,0}(1+z)^3}{E^2(z)}.
```

The exact overdensity used by `Delta_vir()` is

```{math}
:label: gal-overdensity
x=\Omega_m(z)-1,\qquad
\Delta_{\rm code}(z)=\frac{18\pi^2+82x-39x^2}{\Omega_m(z)}.
```

`calculate_Rvir()` and `calculate_Vvir()` then evaluate

```{math}
:label: gal-virial-radius
\rho_{\rm crit}(z)=\frac{3H^2(z)}{8\pi G},\qquad
R_{\rm vir}=\left[\frac{3M_{\rm vir}}{4\pi\Delta_{\rm code}\rho_{\rm crit}}\right]^{1/3},
\qquad V_{\rm vir}=\left(\frac{GM_{\rm vir}}{R_{\rm vir}}\right)^{1/2}.
```

These expressions state the helper convention literally: the source divides the overdensity fit by $\Omega_m(z)$ and combines it with `rhocrit`. Do not replace $\Delta_{\rm code}$ with a differently normalised catalogue overdensity when reproducing this calculation. A tree reader can instead retain catalogue virial properties. The `gbpTrees` reader uses particle-count subhalo masses/radii by default; `FlagSubhaloVirialProps=1` selects its catalogue-value path for the central subhalo. The VELOCIraptor reader retains supplied masses and radii, deriving missing radii and velocities through these helpers; it does not use that selector in its conversion routine.

`calculate_Mvir()` uses the catalogue mass only when `len < 0` and a positive mass is supplied; otherwise $M_{\rm vir}=N_p m_p$, where $N_p$ is the halo particle count and $m_p$ is `PartMass`.

An optional tabulated `MassRatioModifier` changes FOF mass using

```{math}
:label: gal-halo-mass-modifier
\ell_M=\log_{10}\left(\frac{M_{\rm vir,FOF}^{\rm unmodified}}{h}\right)+10,\qquad
M_{\rm vir,FOF}=f_M(\ell_M)M_{\rm vir,FOF}^{\rm unmodified}.
```

Masses in $\ell_M$ are numerical internal values. This correction is separate from the baryon-fraction modifier below. `gbpTrees` recomputes a corrected group's radius; the VELOCIraptor conversion recomputes radius only if the supplied value is missing (`-1`). These tables are associated with the halo-suppression development in [Qin et al. (2017), DRAGONS VIII](https://arxiv.org/abs/1701.03538).

The spin and exponential-disk scale length are

```{math}
:label: gal-disk-radius
\lambda=\frac{j_{\rm halo}}{\sqrt{2}\,V_{\rm vir}R_{\rm vir}},\qquad
R_d=\frac{\lambda R_{\rm vir}}{\sqrt{2}},\qquad
R_{\rm SF}=3R_d.
```

Here `halo->AngMom` supplies $j_{\rm halo}$. Centrals update $V_{\max}$ and $R_d$ from their current haloes. Satellites can retain their infall values with `Flag_FixVmaxOnInfall` and `Flag_FixDiskRadiusOnInfall`.

Atomic-cooling and molecular-cooling halo temperatures follow

```{math}
:label: gal-virial-temperature
T_{\rm vir,AC}=35.9\left(\frac{V_{\rm vir}}{\mathrm{km\,s^{-1}}}\right)^2\mathrm{K},\qquad
T_{\rm vir,MC}=\min\left[73.8\left(\frac{V_{\rm vir}}{\mathrm{km\,s^{-1}}}\right)^2,10^4\right]\mathrm{K}.
```

The inverse threshold helper is

```{math}
:label: gal-temperature-mass
\frac{M_{\rm vir}(T,z)}{10^{10}h^{-1}M_\odot}
=0.01\left(\frac{\mu}{0.6}\right)^{-3/2}
\left[\frac{\Omega_{m,0}}{\Omega_m(z)}\frac{\Delta_{\rm code}(z)}{18\pi^2}\right]^{-1/2}
\left(\frac{T}{1.98\times10^4\mathrm{K}}\right)^{3/2}
\left(\frac{1+z}{10}\right)^{-3/2},
```

with $\mu=1.22$ below approximately $10^4$ K and $\mu=0.59$ above it.

Source: [`virial_properties.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/virial_properties.c), [`init.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/init.c), [`gbpTrees reader`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos-gbptrees.c), [`VELOCIraptor reader`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_halos-velociraptor.c).

## Order of operations

`evolve_galaxies()` first prepares age- and metallicity-dependent feedback tables for the current snapshot. It then processes each occupied FOF group in this order:

1. Calculate the group's infall budget and collect satellite hot/ejected gas onto the central.
2. For the central, calculate a cooling budget using its existing hot gas, add the assigned infall, reincorporate ejected gas, and transfer the cooling mass to cold gas.
3. For every active galaxy, apply delayed stellar feedback when `Flag_IRA=0`, process queued black-hole accretion, and form stars in situ.
4. Decrement orphan merger clocks and process mergers after the galaxy pass.

For an identified galaxy,

```{math}
:label: gal-evolution-timestep
\delta t=\frac{t_{\rm lookback}(\mathrm{LastIdentSnap})-t_{\rm lookback}(\mathrm{snapshot})}{N_{\rm Steps}}.
```

The source distributes the group's infall budget equally among `NSteps`; startup validation enforces `NSteps=1` in this version. A reidentified halo can span more than one catalogue interval, so its $\delta t$ need not equal the neighbouring-snapshot interval. Cooling is estimated **before** the current infall and reincorporation are added. This ordering is part of the implemented prescription.

See [execution flow](workflow.md) for the surrounding halo-reconnection and IGM-feedback steps.

## Baryonic infall and stripping

`gas_infall()` sums the existing baryons over every galaxy in the FOF group:

```{math}
:label: gal-baryon-budget
M_{b,\rm FOF}=\sum_g\left(M_{\star,g}+M_{\rm cold,g}+M_{\rm hot,g}
+M_{\rm ej,g}+M_{\rm BH,g}+M_{\rm BH,queued,g}\right).
```

The mini-halo build also includes `Remnant_Mass`. Gross formed stellar mass is excluded, because it would double-count mass already returned to gas.

Let $f_b$ denote `BaryonFrac`, $f_{\rm UVB}$ the [photoheating infall modifier](igm.md), and $f_{b,\rm tab}$ an optional tabulated baryon-fraction modifier. Then

```{math}
:label: gal-infall
f_{b,\rm eff}=f_{\rm UVB}f_{b,\rm tab},\qquad
\Delta M_{\rm infall}=f_{b,\rm eff}f_bM_{\rm vir,FOF}-M_{b,\rm FOF}.
```

Without a modifier file, $f_{b,\rm tab}=1$. If a file is present, its interpolation coordinate is

```{math}
:label: gal-baryon-modifier-coordinate
\ell=\log_{10}\left(\frac{M_{\rm vir,FOF}}{f_Mh}\right)+10,
```

where masses in this expression are internal numbers and $f_M$ is `FOFMvirModifier`. Between adjacent tabulated centres $\ell_i$, interpolation is linear,

```{math}
:label: gal-modifier-interpolation
f(\ell)=f_i+\frac{f_{i+1}-f_i}{\ell_{i+1}-\ell_i}(\ell-\ell_i),
```

with the endpoint value used outside the table. The source assumes a fixed centre spacing `DELTA_M` when evaluating the denominator.

Positive infall enters the central's hot gas. Negative infall strips ejected gas first, then hot gas, preserving each stripped reservoir's current metallicity; it does not directly remove cold gas or stars. If the tree marks a group below the virial threshold, its hot gas is moved to ejected gas and no new infall occurs. Satellite hot and ejected gas, including their metals, are collected by the FOF central before this update.

With optional external metal enrichment, positive infall also adds $Z_{\rm IGM}\Delta M_{\rm infall}$ to hot-gas metals for an externally enriched central. The enrichment flag and $Z_{\rm IGM}$ are described under [optional physics](optional-physics.md).

Source: [`infall.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/infall.c), [`modifiers.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/modifiers.c).

## Radiative cooling

### Atomic cooling

For $T_{\rm vir}\geq10^4$ K, the model reads the metallicity-dependent `SD93.hdf5` cooling table. It interpolates $\log_{10}\Lambda$ first in $\log_{10}T$, then in $\log_{10}Z$, and exponentiates the result. The eight metallicity tracks are expressed relative to $Z_\odot=0.02$; the temperature grid spans $10^4$–$10^{8.5}$ K. Metallicity is clamped to the available tracks; above the temperature grid, the last interval is extrapolated.

The hot-gas density is an isothermal profile truncated at $R_{\rm vir}$,

```{math}
:label: gal-hot-profile
\rho_{\rm hot}(r)=\frac{M_{\rm hot}}{4\pi R_{\rm vir}r^2},\qquad
t_{\rm dyn,h}=\frac{R_{\rm vir}}{V_{\rm vir}}.
```

Setting the local cooling time equal to $t_{\rm dyn,h}$ gives

```{math}
:label: gal-cooling-radius
\rho(r_{\rm cool})=\frac{3\mu m_pk_BT_{\rm vir}}{2\Lambda(T_{\rm vir},Z_{\rm hot})t_{\rm dyn,h}},\qquad
r_{\rm cool}=\left[\frac{M_{\rm hot}}{4\pi R_{\rm vir}\rho(r_{\rm cool})}\right]^{1/2}.
```

For atomic cooling the numerical coefficient $3\mu/2$ is `0.885`. The code converts $m_pk_BT/\Lambda$ to internal density-times-time units before calculating the radius.

Let $f_{\rm cool}$ be `MaxCoolingMassFactor`. The cooling budget is

```{math}
:label: gal-cooling-mass
\Delta M_{\rm cool,0}=\min\left[
M_{\rm hot},\;
f_{\rm cool}\frac{M_{\rm hot}\delta t}{t_{\rm dyn,h}}
\min\left(1,\frac{r_{\rm cool}}{R_{\rm vir}}\right)
\right].
```

Thus $r_{\rm cool}>R_{\rm vir}$ yields a supply-limited cooling rate; smaller radii yield slow cooling. [Radio-mode black-hole heating](black-holes.md) subtracts a heated mass when `Flag_BHFeedback=1`. The remaining budget is clamped non-negative and rechecked against the available hot gas at transfer time:

```{math}
:label: gal-cooling-transfer
\Delta M_{\rm cool}=\min\left[M_{\rm hot},\max(0,\Delta M_{\rm cool,0}-\Delta M_{\rm heat,BH})\right],
\qquad \Delta M_{Z,\rm cool}=Z_{\rm hot}\Delta M_{\rm cool}.
```

Cooling removes these masses from hot gas and adds them to cold gas. `Rcool` and `Mcool` record the calculated radius and actual transferred mass.

### Molecular cooling in the mini-halo build

When `USE_MINI_HALOS=ON`, a halo below the atomic threshold can cool if its recomputed molecular temperature satisfies $T_{\rm vir,MC}\geq10^3$ K and its halo mass exceeds `MvirCrit_MC`. The [LW/streaming-velocity model](optional-physics.md) supplies that mass threshold. Otherwise its cooling budget is zero. Without the mini-halo build, all sub-atomic-threshold cooling is disabled.

The molecular branch uses $\mu=1.22$, giving $3\mu/2=1.83$, and replaces $\Lambda$ with the following Galli–Palla-type fit. Define $T_3=T/10^3\mathrm{K}$ and adopt $n_H=100\,\mathrm{cm^{-3}}$ in this interpolation:

```{math}
:label: gal-molecular-lte
\begin{aligned}
\Lambda_{r,\rm LTE}&=\frac{1}{n_H}\left[
\frac{9.5\times10^{-22}T_3^{3.76}}{1+0.12T_3^{2.1}}
\exp\!\left(-\left[\frac{0.13}{T_3}\right]^3\right)
+3\times10^{-24}\exp\!\left(-\frac{0.51}{T_3}\right)\right],\\
\Lambda_{v,\rm LTE}&=\frac{1}{n_H}\left[
6.7\times10^{-19}\exp\!\left(-\frac{5.86}{T_3}\right)
+1.6\times10^{-18}\exp\!\left(-\frac{11.7}{T_3}\right)\right],\\
\Lambda_{\rm LTE}&=\Lambda_{r,\rm LTE}+\Lambda_{v,\rm LTE}.
\end{aligned}
```

```{math}
:label: gal-molecular-cooling
\begin{aligned}
\log_{10}\Lambda_{\rm low}&=-103+97.59\log_{10}T
-48.05(\log_{10}T)^2+10.8(\log_{10}T)^3-0.9032(\log_{10}T)^4,\\
\Lambda_{\rm MC}&=\frac{\Lambda_{\rm LTE}}{1+\Lambda_{\rm LTE}/\Lambda_{\rm low}}.
\end{aligned}
```

The fitting coefficients are used with temperature numerically in kelvin and cooling coefficients in the source's cgs convention. The subsequent density, cooling-radius and cooling-mass calculations are identical to the atomic branch.

Source: [`physics/cooling.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/cooling.c), [`core/cooling.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/cooling.c). The mini-halo development is described by [Ventura et al. (2024)](https://arxiv.org/abs/2401.07396).

## Reincorporation

Only a central with positive ejected gas and `ReincorporationEff > 0` reincorporates gas. `ReincorporationModel` selects one of two laws:

```{math}
:label: gal-reincorporation-one
\text{Model 1:}\qquad
\Delta M_{\rm reinc}=\min\left[M_{\rm ej},\;
\epsilon_{\rm reinc}M_{\rm ej}\frac{\delta t}{t_{\rm dyn,h}}\right].
```

Here $\epsilon_{\rm reinc}$ is a dimensionless efficiency. Model 2 interprets the same input as a timescale normalisation $\gamma_{\rm reinc}$ in Myr:

```{math}
:label: gal-reincorporation-two
\text{Model 2:}\qquad
t_{\rm reinc}=\max\left[t_{\rm dyn,h},\;
\gamma_{\rm reinc}\frac{10^{10}M_\odot}{M_{\rm vir,FOF}^{\rm physical}}\right],\qquad
\Delta M_{\rm reinc}=\min\left[M_{\rm ej},\;M_{\rm ej}\frac{\delta t}{t_{\rm reinc}}\right].
```

The mass ratio in the timescale is dimensionless; the source uses the numerical internal mass divided by `Hubble_h` and converts Myr back to internal time. Both models transfer $Z_{\rm ej}\Delta M_{\rm reinc}$ from ejected metals to hot metals.

Model 1 is labelled Guo-type in the source; Model 2 follows the halo-mass-dependent Henriques-type prescription. An unsupported model aborts. Model 2 also explicitly aborts in the mini-halo build. The shipped default efficiency is zero, so reincorporation is disabled until overridden.

Source: [`reincorporation.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/reincorporation.c).

## In-situ star formation

### Disk-velocity selector

`SfDiskVelOpt=1` uses $V_d=V_{\max}$; `2` uses $V_d=V_{\rm vir}$. An unrecognised value logs a message and falls back to $V_{\max}$. Define the disk dynamical time and redshift-dependent efficiency as

```{math}
:label: gal-sf-efficiency
t_{\rm dyn,d}=\frac{R_{\rm SF}}{V_d},\qquad
\alpha_{\rm SF}(z)=\mathrm{SfEfficiency}\,(1+z)^{\mathrm{SfEfficiencyScaling}}.
```

### Prescription 1: critical surface density

The default law uses a critical cold-gas mass,

```{math}
:label: gal-critical-sf
M_{\rm crit}=\mathrm{SfCriticalSDNorm}\,V_dR_{\rm SF},\qquad
\Delta M_{\star,0}=\alpha_{\rm SF}(z)
\frac{[M_{\rm cold}-M_{\rm crit}]_+}{t_{\rm dyn,d}}\delta t,
```

where $[q]_+=\max(q,0)$. The first equation is a numerical internal-unit prescription: `SfCriticalSDNorm` incorporates the conversion associated with the surface-density threshold. `V_d` is numerically in $\mathrm{km\,s^{-1}}$, $R_{\rm SF}$ in $h^{-1}\mathrm{Mpc}$, and $M_{\rm crit}$ in $10^{10}h^{-1}M_\odot$.

With `USE_MINI_HALOS`, Population III uses `SfEfficiency_III`, `SfEfficiencyScaling_III` and `SfCriticalSDNorm_III` instead. `SfPrescription=1` is the supported mini-halo setting. The parser contains a reset to this value, but executes it before loading parameter-file values, so an explicit alternative can overwrite the reset; set the value explicitly rather than relying on that ordering.

### Prescription 2: pressure-dependent molecular gas

The alternative pressure law represents gas and stars by exponential disks of scale length $R_d$. In the routine's converted SI values,

```{math}
:label: gal-pressure-surfaces
\Sigma_{g,0}=\frac{0.76M_{\rm cold}}{2\pi R_d^2},\qquad
\Sigma_{\star,0}=\frac{M_\star}{2\pi R_d^2},\qquad
\Sigma_g(r)=\Sigma_{g,0}e^{-r/R_d},\qquad
\Sigma_\star(r)=\Sigma_{\star,0}e^{-r/R_d}.
```

The `0.76` hydrogen fraction is fixed in the surface-density calculation. The disk integration uses

```{math}
:label: gal-pressure-molecular-fraction
\begin{aligned}
C_\sigma&=\frac{10^4\,\mathrm{m\,s^{-1}}}{\sqrt{\pi G(0.14R_d)}},\\
P_{\rm ext}(r)&=\frac{\pi G}{2}\Sigma_g(r)
\left[\Sigma_g(r)+C_\sigma\sqrt{\Sigma_\star(r)}\right],\\
f_{\rm mol}(r)&=\left[1+\left(\frac{P_{\rm ext}(r)}{4.79\times10^{-13}\,\mathrm{Pa}}\right)^{-0.92}\right]^{-1}.
\end{aligned}
```

The molecular mass and star-formation rate are

```{math}
:label: gal-pressure-sf-integral
M_{\rm H_2,int}=2\pi\int_0^{5R_d}r\,f_{\rm mol}(r)\Sigma_g(r)\,dr,\qquad
\dot M_{\star,0}=\frac{\alpha_{\rm SF}(z)}{3\times10^8\,\mathrm{yr}}M_{\rm H_2,int}.
```

The integral is evaluated with GSL adaptive quadrature. The stored gas components are

```{math}
:label: gal-hydrogen-masses
M_{\rm H_2}=\min\left[M_{\rm H_2,int},(1-Y_{\rm He})M_{\rm cold}\right],\qquad
M_{\rm HI}=(1-Y_{\rm He})M_{\rm cold}-M_{\rm H_2}.
```

`H2Frac` stores **the central** value $f_{\rm mol}(0)$, whereas `H2Mass` is the capped disk-integrated mass. Therefore `H2Frac` is not generally `H2Mass / ((1-Y_He)*ColdGas)`. The SFR uses the integral before the stored `H2Mass` cap. Zero disk radius or non-positive gas surface density returns zero SFR and zero stored hydrogen components.

The depletion time implied by the coefficient is $3\times10^8/\alpha_{\rm SF}(z)$ yr: `SfEfficiency=0.15` gives 2 Gyr at zero efficiency scaling, and `1` gives 300 Myr. This follows the executable expression, rather than the `300Gyr` typo in the parameter-file comment.

### Prescription 3: GALFORM-style timescale

The third implemented law is

```{math}
:label: gal-galform-sf
\tau_\star=\frac{t_{\rm dyn,d}}{0.029}
\left(\frac{200\,\mathrm{km\,s^{-1}}}{V_d}\right)^{1.5},\qquad
\Delta M_{\star,0}=\frac{M_{\rm cold}}{\tau_\star}\delta t.
```

This branch uses its fixed coefficient and velocity scaling; it does not multiply by `SfEfficiency`, `SfEfficiencyScaling` or a critical cold-gas threshold. Unsupported `SfPrescription` values abort.

### Formed mass and reservoir update

All prescriptions first cap the proposed formed mass at the available cold gas. Contemporaneous feedback can reduce it further. The accepted formed mass $\Delta M_\star$ updates the reservoirs as

```{math}
:label: gal-sf-reservoir-update
\begin{aligned}
M_{\rm cold}&\leftarrow M_{\rm cold}-\Delta M_\star,&
M_{Z,\rm cold}&\leftarrow M_{Z,\rm cold}-Z_{\rm cold}\Delta M_\star,\\
M_\star&\leftarrow M_\star+\Delta M_\star,&
M_{Z,\star}&\leftarrow M_{Z,\star}+Z_{\rm cold}\Delta M_\star,\\
M_{\star,\rm gross}&\leftarrow M_{\star,\rm gross}+\Delta M_\star,&
\mathrm{Sfr}&\leftarrow\mathrm{Sfr}+\frac{\Delta M_\star}{\delta t}.
\end{aligned}
```

The cold-gas metallicity is measured before gas is consumed. Recycling is applied after this update, so the surviving stellar mass increase is subsequently reduced by returned mass. Population III maintains its own gross mass and SFR fields. `Sfr` is reset at each snapshot and accumulates contributions from in-situ formation and merger bursts; the grid writers perform the output-rate unit conversion.

The same accepted formed mass updates recent stellar-history bins, [escape-weighted source quantities](stochasticity.md), and enabled [photometry/emission-line calculations](optional-physics.md). For a reidentified ghost in the delayed-feedback treatment, in-situ formation is backfilled into the historical bin containing the assumed midpoint burst rather than always inserted into the present bin.

Source: [`star_formation.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/star_formation.c).

## Stellar recycling and supernova feedback

### Metallicity and feedback tables

The generic metallicity helper uses

```{math}
:label: gal-metallicity
Z=\begin{cases}
\min[1,\max(0,M_Z/M)] & M>0\ \mathrm{and}\ M_Z>0,\\
0 & \mathrm{otherwise}.
\end{cases}
```

`stellar_feedback_tables.hdf5` supplies age, total returned-mass rate, returned-metal rate and cumulative supernova energy for single-age stellar populations. The implementation has 40 metallicity bins and 2000 age samples; it integrates yield rates over the current feedback interval and differences the cumulative-energy table.

Let $m_i$ be formed stellar mass in history bin $i$, $Z_i$ its initial metallicity, $[a_i,b_i]$ its age interval during the current snapshot, $\dot R(a,Z)$ the mass-return kernel, $\dot Y_Z(a,Z)$ the metal-return kernel, and $\mathcal E(a,Z)$ cumulative SN energy per formed mass. Then

```{math}
:label: gal-feedback-kernels
R_i(Z)=\int_{a_i}^{b_i}\dot R(a,Z)\,da,\qquad
Y_i(Z)=\int_{a_i}^{b_i}\dot Y_Z(a,Z)\,da,\qquad
e_i(Z)=\mathcal E(b_i,Z)-\mathcal E(a_i,Z).
```

```{math}
:label: gal-delayed-feedback
\Delta M_{\rm rec}=\sum_i m_iR_i(Z_i),\qquad
\Delta M_{Z,\rm ret}=\sum_i m_iY_i(Z_i),\qquad
E_{\rm SN,raw}=\sum_i m_i e_i(Z_i).
```

Current star formation is approximated as a midpoint burst. For an earlier burst, `compute_stellar_feedback_tables()` derives its age at the beginning and end of the present interval from the midpoint of its formation snapshots. In lookback-time notation, for current snapshot $s$ and history index $i>0$,

```{math}
:label: gal-feedback-ages
a_i=\frac{L_{s-i-1}+L_{s-i}}{2}-L_{s-1},\qquad
b_i=\frac{L_{s-i-1}+L_{s-i}}{2}-L_s,
```

where $L_j=t_{\rm lookback}(j)$, converted to Myr. The current bin starts at the first age-table entry and ends at half the current snapshot interval. Yield rates use tabulated trapezoidal integration. Metallicity is mapped to $\mathrm{clamp}(\mathrm{int}(1000Z-0.5),0,39)$; no continuous metallicity interpolation is applied in this lookup. If the end age reaches the last tabulated age, the source sets that working-bin contribution to zero.

`N_HISTORY_SNAPS` is a compile-time history capacity, default 17. At startup, the code checks that it spans the required SN-energy release for the supplied snapshot cadence and table. Prior history bins are processed only with `Flag_IRA=0`; contemporaneous feedback handles bin zero.

### Instantaneous recycling approximation

With `Flag_IRA=1`, current-burst recycling and metal return use constant input fractions:

```{math}
:label: gal-ira
\Delta M_{\rm rec}=\mathrm{SfRecycleFraction}\,\Delta M_\star,\qquad
\Delta M_{Z,\rm ret}=\mathrm{Yield}\,\Delta M_\star.
```

The mini-halo build substitutes the `_III` parameters for Population III. This switch replaces recycling/yield kernels and disables feedback from older bursts. **The current-burst SN energy still uses `get_SN_energy(0, metallicity)`**; the switch does not replace it with the full lifetime SN energy.

### Reheating and energy-coupling efficiencies

Two independent efficiency families control the reheated mass, $\epsilon_{\rm rh}$, and the available SN energy, $\epsilon_E$. For `SnModel=1`, each has the form

```{math}
:label: gal-sn-guo
\epsilon_q(V_{\max},z)=\epsilon_{q,0}
\left(\frac{1+z}{4}\right)^{\beta_q}
\left[0.5+\left(\frac{V_{\max}}{V_q}\right)^{-\alpha_q}\right],
\qquad q\in\{\mathrm{rh},E\}.
```

For `SnModel=2`, the broken-power-law form is

```{math}
:label: gal-sn-muratov
\epsilon_q(V_{\max},z)=\epsilon_{q,0}
\left(\frac{1+z}{4}\right)^{\beta_q}
\left(\frac{V_{\max}}{V_q}\right)^{-\alpha_q(V_{\max})},\qquad
\alpha_q(V)=\begin{cases}\alpha_{q,\rm low},&V<V_q,\\\alpha_{q,\rm high},&V\geq V_q.\end{cases}
```

The reheating family maps to `SnReheatEff`, `SnReheatRedshiftDep`, `SnReheatNorm`, `SnReheatScaling`, and `SnReheatScaling2`; the energy family maps to the corresponding `SnEjection*` parameters. The source labels Model 1 Guo-type and Model 2 Muratov-type. The final caps are

```{math}
:label: gal-sn-caps
\epsilon_{\rm rh}\leftarrow\min(\epsilon_{\rm rh},\mathrm{SnReheatLimit}),\qquad
\epsilon_E\leftarrow\min(\epsilon_E,1).
```

The current implementation reads the reheating and ejection velocity normalisations independently. Despite a comment in `defaults.par`, it does not force `SnEjectionNorm = SnReheatNorm`. For Population III the high-velocity coefficients are selected from `_III` parameters; the low-velocity exponent in Model 2 is read from the unsuffixed `SnReheatScaling2` or `SnEjectionScaling2` in these functions.

For Population II, let $e_{\rm SN,tot}$ denote the lifetime SN energy per formed mass returned by `get_total_SN_energy()`. Then

```{math}
:label: gal-sn-reheating
\Delta M_{\rm rh,0}=\epsilon_{\rm rh}\frac{E_{\rm SN,raw}}{e_{\rm SN,tot}},\qquad
E_{\rm SN}=\epsilon_E E_{\rm SN,raw}.
```

Both delayed and contemporaneous routines cap the proposed reheated mass against current cold gas before solving the energy budget.

### Energy-limited reheating and ejection

Set $V_h=V_{\rm vir,gal}$, or $V_h=V_{\rm vir,FOF}$ when `Flag_ReheatToFOFGroupTemp=1`. The initial host-halo energy check is

```{math}
:label: gal-sn-energy-host
E_{\rm rh,h}=\frac12\Delta M_{\rm rh}V_h^2,\qquad
\Delta M_{\rm ej,h}=\frac{E_{\rm SN}-E_{\rm rh,h}}{V_h^2/2}.
```

If this is non-positive, there is no ejection and the reheated mass is reduced to $2E_{\rm SN}/V_h^2$. If it is positive and a FOF velocity is available, the ejected mass is recomputed in the group potential:

```{math}
:label: gal-sn-energy-ejection
\Delta M_{\rm ej}=\left[\frac{2E_{\rm SN}}{V_{\rm vir,FOF}^2}-\Delta M_{\rm rh}\right]_+.
```

An additional reservoir cap prevents ejection of more gas than the central currently has in its hot phase. `calc_ejected_mass()` returns zero when the reheated mass is zero. For ghosts, reheated gas enters the ghost's retained hot reservoir, and the subsequent ejection update is skipped because the current host potential is unknown.

### Availability limiter and reservoir update

Before a current burst is committed, the code checks the simultaneous demands from star formation and reheating. If their sum exceeds the original cold gas,

```{math}
:label: gal-sn-availability
f_{\rm avail}=\frac{M_{\rm cold}}{\Delta M_{\rm rh}+\Delta M_\star}<1,
```

and multiplies formed stars, reheated mass, recycled mass and remnant mass by this factor. In this source version, the precomputed metal return and SN energy are not multiplied by $f_{\rm avail}$. Reproducing the executed branch therefore requires retaining those values; treating every feedback quantity as proportional to the final accepted stellar mass gives a different result.

After star formation has been added, recycled mass is removed from stars and returned to cold gas. Returned metals enter cold gas when cold gas is non-negligible, otherwise the central's hot metal reservoir. Define $f_{Z,\rm ret}$ as `SnMetalRetentionFraction`; gas reheating then transfers

```{math}
:label: gal-sn-metal-transfer
\Delta M_{Z,\rm rh}=(1-f_{Z,\rm ret})Z_{\rm cold}\Delta M_{\rm rh},\qquad
\Delta M_{Z,\rm ej}=Z_{\rm hot,central}\Delta M_{\rm ej}.
```

The untransferred reheated-gas metals remain in the cold reservoir. Gas is added to the FOF central's hot reservoir before the ejected fraction is moved into that central's ejected reservoir. All relevant gas, stellar and metal reservoirs are clamped non-negative after the update.

`MetalsStellarMass` is increased by the metals initially locked in newly formed stars, but the feedback routine subtracts the returned-metal quantity. The source explicitly identifies this stellar-metal bookkeeping as unsuitable for physical stellar-metallicity interpretation; it does not affect the subsequent galaxy-evolution prescriptions. Cold- and hot-gas metallicities are the quantities used for cooling and feedback-table lookup.

### Population III conditional extension

The optional build distinguishes core-collapse and pair-instability supernova channels and direct-collapse remnants. Let $m_{\star,III}$ be the formed Population III mass, $F_{\rm CC}$, $F_{\rm PI}$, and $F_{\rm BH}$ the IMF mass fractions in those channels, and $r_{\rm CC,i}$, $y_{\rm CC,i}$, $q_{\rm CC,i}$ their implemented return, metal and remnant factors. For delayed core-collapse feedback,

```{math}
:label: gal-popiii-delayed
\Delta M_{\rm rec,III}=\sum_{i>0}m_{\star,III,i}F_{\rm CC}r_{\rm CC,i},\qquad
\Delta M_{Z,III}=\sum_{i>0}m_{\star,III,i}F_{\rm CC}y_{\rm CC,i},\qquad
\Delta M_{\rm rem}=\sum_{i>0}m_{\star,III,i}F_{\rm CC}q_{\rm CC,i}.
```

For a contemporaneous burst with delayed-return tables,

```{math}
:label: gal-popiii-current
\begin{aligned}
\Delta M_{\rm rec,III}&=m_{\star,III}\left(F_{\rm CC}r_{\rm CC,0}+F_{\rm PI}r_{\rm PI}\right),\\
\Delta M_{\rm rem}&=m_{\star,III}\left(F_{\rm BH}+F_{\rm CC}q_{\rm CC,0}\right),\\
\Delta M_{Z,III}&=m_{\star,III}F_{\rm CC}y_{\rm CC,0}
+\left[m_{\star,III}F_{\rm PI}y_{\rm PI}-20M_\odot\right]_+.
\end{aligned}
```

The final term is the explicit fixed-mass subtraction in this branch, converted to internal units in the source. Pair-instability feedback is contemporaneous; only core-collapse feedback is delayed. Population III reheating is proportional to the implemented number of supernova events,

```{math}
:label: gal-popiii-reheat
\Delta M_{\rm rh,III}=\epsilon_{\rm rh,III}m_{\star,III}
\left(\frac{e_{\rm CC,0}}{E_{\rm CC}}+\frac{e_{\rm PI}}{E_{\rm PI}}\right),
```

where $e$ is the corresponding energy per formed mass and $E_{\rm CC}$, $E_{\rm PI}$ are the channel energies per event. Delayed feedback uses the core-collapse term alone. To reproduce the source's energy conversion exactly, write $m_i$ as a numerical internal mass, $N_{\rm CC}$ as `NumberSNII`, $\kappa_M=10^{10}/h$, and $e_{\rm CC,i}^{\rm cgs}$ as the energy returned by `get_SN_energy_PopIII(i, snapshot, 0)`. Then

```{math}
:label: gal-popiii-energy-conversion
\begin{aligned}
S_{\rm III}&=\sum_{i>0}m_i e_{\rm CC,i}^{\rm cgs},\\
E_{\rm SN,III}^{\rm delayed}&=\epsilon_{E,III}
\frac{S_{\rm III}N_{\rm CC}\kappa_M}{U_E},\\
E_{\rm SN,III}^{\rm current}&=\epsilon_{E,III}
\frac{m_0(e_{\rm CC,0}^{\rm cgs}+e_{\rm PI}^{\rm cgs})}{U_E}.
\end{aligned}
```

The delayed routine applies the extra $N_{\rm CC}\kappa_M$ factor even though the core energy helper already includes it. This is a difference between the executed delayed and current-burst branches; the equations do not remove that factor. These quantities require the IMF/lifetime integrals defined in [`PopIII.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/PopIII.c); the [optional-physics reference](optional-physics.md) gives their definitions and the separate SN-driven metal-bubble prescription.

Source: [`supernova_feedback.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/supernova_feedback.c), [`stellar_feedback.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/stellar_feedback.c).

## Galaxy mergers

### Dynamical-friction clock

Once a galaxy becomes an orphan, `calculate_merging_time()` chooses the less massive halo by particle count as the satellite and identifies the most massive participating halo as the merger's mother halo. The satellite mass in the friction formula is its halo `Mvir`; cold gas and stellar mass are not added again.

With satellite–mother separation $r_{\rm com}$,

```{math}
:label: gal-merger-separation
r_{\rm phys}=\frac{r_{\rm com}}{1+z_{s-1}},\qquad
r=\min(r_{\rm phys},R_{\rm vir,mother}),\qquad
\ln\Lambda=\ln\left(1+\frac{N_{p,\rm mother}}{N_{p,\rm sat}}\right).
```

The distance helper applies periodic boundaries. The previous snapshot's redshift is used even for a halo that has skipped catalogue snapshots. `MergerStartRadius` stores the uncapped $r_{\rm phys}/R_{\rm vir,mother}$.

```{math}
:label: gal-merger-time
t_{\rm merge}=\mathrm{MergerTimeFactor}\,
\frac{1.17r^2V_{\rm vir,mother}}{\ln\Lambda\,GM_{\rm vir,sat}}.
```

The routine returns a negative sentinel (`-999`) for immediate processing if either galaxy has negligible stellar-plus-cold mass, or if the smaller stellar mass is below `MinMergerStellarMass`. Each active evolution step subtracts $\delta t$ from `MergTime`. A merger is processed when its clock is negative or its previous target is already merged; in the latter case the surviving target is found by following the target chain.

### Merger ratio and induced starburst

The burst and black-hole triggers use a **baryonic** ratio, evaluated before the galaxies are combined:

```{math}
:label: gal-merger-ratio
B_g=M_{\star,g}+M_{\rm cold,g},\qquad
\mu_{\rm merge}=\frac{\min(B_1,B_2)}{\max(B_1,B_2)}.
```

The mini-halo build includes remnant mass in $B_g$. After adding the reservoirs, a burst occurs when the smaller stellar mass meets `MinMergerStellarMass`, the ratio exceeds `MinMergerRatioForBurst`, and cold gas is available:

```{math}
:label: gal-merger-burst
\Delta M_{\star,\rm burst,0}=\min\left[
M_{\rm cold,combined},\;
\mathrm{MergerBurstFactor}\,\mu_{\rm merge}^{\mathrm{MergerBurstScaling}}
M_{\rm cold,combined}\right].
```

The burst passes through the same contemporaneous feedback and availability limiter as in-situ star formation. The accepted mass contributes to `MergerBurstMass`, the SFR and the stellar-source history. Enabled merger-driven black-hole growth is processed afterwards.

`ThreshMajorMerger` is parsed and present in the default file, but the current merger routine does not use it to split these equations into major- and minor-merger branches. Burst triggering is controlled by `MinMergerRatioForBurst`.

### Inherited quantities

The surviving galaxy receives the progenitor's gas, stellar and metal reservoirs, gross formed stellar mass, source accumulators, SFR, recent star-formation/metal-history bins, black-hole reservoirs and enabled luminosity quantities. Stochasticity-treated and no-scatter cumulative histories are also added when that build option is enabled. Consequently, cumulative sources include the surviving galaxy's entire assembled progenitor history, rather than only stars formed on its current main branch. The merged object becomes `Type=3` and is later removed from the active list.

Source: [`mergers.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics/mergers.c).

## Runtime controls and shipped defaults

The values below are the generic defaults in [`input/params/defaults.par`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/input/params/defaults.par), not a calibrated configuration for a particular simulation. Simulation parameter files and the launch parameter file can override them; see [parameter precedence](inputs.md).

| Parameter | Default | Effect |
|---|---:|---|
| `NSteps` | `1` | Evolution steps per snapshot; startup validation enforces one |
| `FlagSubhaloVirialProps` | `0` | `gbpTrees` central-subhalo choice of particle-count or catalogue virial quantities |
| `Flag_FixVmaxOnInfall` | `0` | Retain satellite infall `Vmax` when enabled |
| `Flag_FixDiskRadiusOnInfall` | `0` | Retain satellite infall disk scale length when enabled |
| `MaxCoolingMassFactor` | `1.0` | Maximum hot-gas cooling rate relative to $M_{\rm hot}/t_{\rm dyn,h}$ |
| `ReincorporationModel` | `1` | Dynamical-time law (`1`) or halo-mass-dependent timescale (`2`) |
| `ReincorporationEff` | `0.0` | Dimensionless Model-1 efficiency or Model-2 Myr normalisation; zero disables both |
| `SfPrescription` | `1` | Critical-density (`1`), pressure-dependent (`2`), or GALFORM-style (`3`) SF law |
| `SfDiskVelOpt` | `1` | `Vmax` (`1`) or `Vvir` (`2`) for the disk velocity |
| `SfEfficiency` | `0.08` | SF normalisation in Prescriptions 1 and 2 |
| `SfEfficiencyScaling` | `0.0` | Power of $1+z$ in the efficiency |
| `SfCriticalSDNorm` | `0.2` | Internal-unit critical gas-mass coefficient in Prescription 1 |
| `Flag_IRA` | `0` | Delayed kernels (`0`) or constant current-burst recycling/yields (`1`) |
| `SfRecycleFraction` | `0.25` | Recycled mass per formed mass in IRA |
| `Yield` | `0.03` | Returned metals per formed mass in IRA |
| `Flag_ReheatToFOFGroupTemp` | `0` | Use FOF rather than galaxy-halo velocity for the first reheating energy check |
| `SnModel` | `1` | Guo-type (`1`) or broken-power-law Muratov-type (`2`) efficiencies |
| `SnReheatEff`, `SnEjectionEff` | `10.0`, `0.5` | Reheating and energy-coupling normalisations |
| `SnReheatRedshiftDep`, `SnEjectionRedshiftDep` | `0.0`, `0.0` | Exponents of $(1+z)/4$ |
| `SnReheatNorm`, `SnEjectionNorm` | `70.0`, `70.0` | Independent velocity normalisations in $\mathrm{km\,s^{-1}}$ |
| `SnReheatScaling`, `SnEjectionScaling` | `0.0`, `2.0` | Model-1 power or Model-2 high-velocity power |
| `SnReheatScaling2`, `SnEjectionScaling2` | `0.0`, `2.0` | Model-2 low-velocity powers |
| `SnReheatLimit` | `10.0` | Maximum reheating efficiency |
| `SnMetalRetentionFraction` | `0.0` | Fraction of reheated-gas metals left in cold gas |
| `MergerTimeFactor` | `0.5` | Dynamical-friction timescale multiplier |
| `MinMergerStellarMass` | `1e-9` | Minimum stellar mass in internal units for a finite clock and induced burst |
| `MinMergerRatioForBurst` | `0.1` | Baryonic-ratio burst threshold |
| `MergerBurstFactor`, `MergerBurstScaling` | `0.57`, `0.7` | Burst efficiency and ratio exponent |
| `ThreshMajorMerger` | `0.3` | Parsed value; not used by the current merger formulas |

Mini-halo-specific defaults include `SfEfficiency_III=0.008`, `SfEfficiencyScaling_III=0`, `SfCriticalSDNorm_III=0.2`, `SfRecycleFraction_III=0.25`, and `Yield_III=0.03`. The `_III` SN coefficients equal their unsuffixed defaults in this file. Population changes use `ZCrit=0.0001` and the source comparison $Z/0.01>\mathrm{ZCrit}$; equality therefore remains on the Population III side of the test. See [optional physics](optional-physics.md) for its enrichment and IMF controls.

## Reading the model's predictions

The physical equations couple gas supply and feedback, so changing one parameter can affect several outputs simultaneously. `StellarMass` tests surviving stellar growth; `GrossStellarMass` and escape-weighted cumulative mass determine cumulative stellar source budgets; `ColdGas`, `HotGas` and `EjectedGas` trace different stages of gas cycling. `Mcool` records transfer in the current step, while `Rcool` is a calculated radius and can exceed `Rvir` in the supply-limited branch.

The H I/H$_2$ properties are updated by the pressure-based SF prescription. They should not be interpreted as a general gas-partition calculation for Prescriptions 1 or 3. For stochasticity experiments, the treatment changes source quantities after galaxy evolution; its interaction with recalibration and cumulative histories is specified on the [stochasticity page](stochasticity.md).

Use the [output reference](outputs.md) for field types, units, metadata and tree-link interpretation, and the [equation index](equations.md) to locate the prescriptions across this guide.
