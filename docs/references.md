(references)=
# References and source provenance

The guide describes the `forests` source revision identified below. Research
papers explain the physical motivation, development and validation of Meraxes;
the pinned source determines the equations, selectors, defaults and output
fields documented here. A citation does not imply that every prescription or
calibration in that paper is implemented unchanged in this revision.

## Documented implementations

| Component | Repository and inspected revision | Scope |
|---|---|---|
| Meraxes | [`qyx268/meraxes-devs`, `forests`, `90d8474cf41dcea646189fb86a65b7e18755ed95`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95) | Program flow, build options, parameter parsing, galaxy/IGM physics, stochasticity and HDF5 writers. |
| Sector | [`meraxes-devs/sector`, `4824becc9ea8e5f7c9728b2445530ab688b386a5`](https://github.com/meraxes-devs/sector/tree/4824becc9ea8e5f7c9728b2445530ab688b386a5) | Independently inspected external SED/filter/dust implementation used to explain the optional Meraxes photometry interface. |

Sector is supplied through `SECTOR_ROOT`; the Meraxes revision does **not** pin
this external repository to the inspected Sector commit. Record the Sector
revision used in an actual build, together with the SED-library files. The
Meraxes tree's `mlog` submodule is a separate dependency. See
[Getting started](getting-started.md) for the build dependencies and
[Optional physics](optional-physics.md) for the photometry interface.

The guide was assembled by tracing the executed call paths and their
compile-time guards, checking accepted parameter names and distributed
defaults, and following the quantities passed between galaxy evolution,
radiation grids and output writers. Algebraic expressions retain the source's
normalizations, units, clipping and update order. Where an expression differs
from a conventional interpretation, the relevant physics page states the
difference. No particular simulation's snapshot count, rank count, galaxy
count or grid inventory defines the generic output schema.

| Question | Source authority |
|---|---|
| Which features are compiled? | [Top-level `CMakeLists.txt`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/CMakeLists.txt), source guards and linked dependencies. |
| Which parameters are accepted and what are their defaults? | [`src/core/read_params.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/read_params.c) and [`input/params/defaults.par`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/input/params/defaults.par). |
| Which physics runs, and in which order? | [`src/core/meraxes.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/meraxes.c), its callees in [`src/core`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core) and [`src/physics`](https://github.com/qyx268/meraxes-devs/tree/90d8474cf41dcea646189fb86a65b7e18755ed95/src/physics). The built-in IGM routines are also in `src/core`. |
| How do stochastic source treatments work? | [`src/core/Stochasticity.c`](https://github.com/qyx268/meraxes-devs/blob/90d8474cf41dcea646189fb86a65b7e18755ed95/src/core/Stochasticity.c), escape-fraction updates and grid construction. |
| What is actually written? | The output writers described and linked in [Outputs](outputs.md); an output file's own metadata and enabled options determine its actual contents. |

For reproducible research, retain the source commit, build options, compiler
and dependency versions, input/simulation/default parameter files, input-tree
and table versions, random seed, MPI layout and external Sector/SED versions
when applicable. Published best-fitting parameters are model calibrations,
which can differ from the distributed defaults.

## Papers and the guide

The upstream README requests citation of Mutch et al. (2016) for Meraxes and
the corresponding development paper when using its AGN, SED/dust, thermal
21-cm or mini-halo features. This table maps those foundations and closely
related developments to the guide.

| Paper | Scientific contribution or context | Guide page | Relationship to this revision |
|---|---|---|---|
| [Mutch et al. (2016), DRAGONS III](#ref-mutch2016) | Coupled semi-analytic galaxy formation and reionization framework. | [Workflow](workflow.md), [Galaxy physics](galaxy-physics.md), [IGM physics](igm.md) | Foundational Meraxes reference. |
| [Qin et al. (2017a), DRAGONS VIII](#ref-qin2017viii) | Suppression of halo growth and baryon content relative to collisionless simulations. | [Inputs](inputs.md), [Galaxy physics](galaxy-physics.md) | Context for the optional halo/baryon correction tables. |
| [Qin et al. (2017b), DRAGONS X](#ref-qin2017x) | Black-hole growth, AGN feedback and quasar ionizing budgets. | [Black holes and AGN](black-holes.md) | AGN feature reference; newer luminosity and obscuration fits are identified separately. |
| [Qin et al. (2018), DRAGONS XIV](#ref-qin2018xiv) | High-redshift dwarf-galaxy gas accretion, cooling and star formation. | [Galaxy physics](galaxy-physics.md) | Development and hydrodynamic-comparison context; selector equations remain source-defined. |
| [Qin et al. (2019), DRAGONS XV](#ref-qin2019xv) | High-redshift stellar evolution and feedback. | [Galaxy physics](galaxy-physics.md) | Development and calibration context; does not make all paper parameter choices defaults. |
| [Qiu et al. (2019), DRAGONS XIX](#ref-qiu2019) | Joint galaxy/dust modelling and predictions from UV observations. | [Optional physics](optional-physics.md) | SED/dust feature reference; the implemented gas-column form and external Sector attenuation are documented explicitly. |
| [Davies et al. (2019), DRAGONS XVI](#ref-davies2019) | Thermal memory following reionization. | [IGM physics](igm.md) | Related thermal-development context; the current field update order is specified from source. |
| [Balu et al. (2023)](#ref-balu2023) | IGM thermal evolution and the 21-cm signal in large-volume Meraxes simulations. | [IGM physics](igm.md) | Thermal/spin-temperature and 21-cm feature reference. |
| [Ventura et al. (2024), Pop. III I](#ref-ventura2024) | Resolved mini-halo Pop. III formation and metallicity evolution. | [Galaxy physics](galaxy-physics.md), [Optional physics](optional-physics.md) | Mini-halo feature reference; activation depends on build and runtime controls. |
| [Marshall et al. (2020), DRAGONS XVIII](#ref-marshall2020) | Black-hole/host evolution, including an extended growth model. | [Black holes and AGN](black-holes.md) | Related development; its disc-instability BH channel is not assumed present in the documented merger/hot-accretion implementation. |
| [Ventura et al. (2025), Pop. III II](#ref-ventura2025) | Unresolved Pop. III modelling and consequences for the 21-cm power spectrum. | [Optional physics](optional-physics.md), [IGM physics](igm.md) | Related development; `USE_MINI_HALOS` alone does not activate all unresolved-source prescriptions in this paper. |
| Current stochasticity implementation | Escape-fraction draws, median-SFR source replacement, X-ray draws and source recalibration. | [Stochasticity](stochasticity.md) | Documented directly from the pinned source; no publication is assigned to an unverified branch-specific prescription. |
| Current [O III] implementation | Ionizing-photon, gas and metallicity calculations for the stored line luminosity. | [Optional physics](optional-physics.md), [Outputs](outputs.md) | Documented from the implemented algebra; no unverified paper is used to assert a different nebular prescription. |

The bibliography below covers these development papers and the principal
prescription references used in the guide. It is not a catalogue of every
Meraxes application. The upstream project links a broader
[Meraxes publication library on ADS](https://ui.adsabs.harvard.edu/public-libraries/CWUcYnt3TsmG6BuOKjR0Fw).

## Meraxes foundations and development

(ref-mutch2016)=
**Mutch, S. J., Geil, P. M., Poole, G. B., Angel, P. W., Duffy, A. R.,
Mesinger, A. & Wyithe, J. S. B. (2016).** *Dark-ages reionization and galaxy
formation simulation – III. Modelling galaxy formation and the epoch of
reionization.* MNRAS **462**, 250–276.
[DOI: 10.1093/mnras/stw1506](https://doi.org/10.1093/mnras/stw1506);
[arXiv:1512.00562](https://arxiv.org/abs/1512.00562).

(ref-qin2017viii)=
**Qin, Y., Duffy, A. R., Mutch, S. J., Poole, G. B., Geil, P. M., Angel,
P. W., Mesinger, A. & Wyithe, J. S. B. (2017a).** *Dark-ages Reionization &
Galaxy Formation Simulation VIII. Suppressed growth of dark matter halos
during the Epoch of Reionization.* MNRAS **467**, 1678–1693.
[DOI: 10.1093/mnras/stx083](https://doi.org/10.1093/mnras/stx083);
[arXiv:1701.03538](https://arxiv.org/abs/1701.03538).

(ref-qin2017x)=
**Qin, Y., Mutch, S. J., Poole, G. B., Liu, C., Angel, P. W., Duffy, A. R.,
Geil, P. M., Mesinger, A. & Wyithe, J. S. B. (2017b).** *Dark-ages
Reionization and Galaxy Formation Simulation – X. The small contribution
of quasars to reionization.* MNRAS **472**, 2009–2027.
[DOI: 10.1093/mnras/stx1909](https://doi.org/10.1093/mnras/stx1909);
[arXiv:1703.04895](https://arxiv.org/abs/1703.04895).

(ref-qin2018xiv)=
**Qin, Y., Duffy, A. R., Mutch, S. J., Poole, G. B., Geil, P. M., Mesinger,
A. & Wyithe, J. S. B. (2018).** *Dark-ages Reionization and Galaxy Formation
Simulation – XIV. Gas accretion, cooling and star formation in dwarf
galaxies at high redshift.* MNRAS **477**, 1318–1335.
[DOI: 10.1093/mnras/sty767](https://doi.org/10.1093/mnras/sty767);
[arXiv:1802.03879](https://arxiv.org/abs/1802.03879).

(ref-qin2019xv)=
**Qin, Y., Duffy, A. R., Mutch, S. J., Poole, G. B., Mesinger, A. & Wyithe,
J. S. B. (2019).** *Dark-ages Reionization and Galaxy Formation Simulation –
XV. Stellar evolution and feedback in dwarf galaxies at high redshift.*
MNRAS **487**, 1946–1963.
[DOI: 10.1093/mnras/stz1380](https://doi.org/10.1093/mnras/stz1380);
[arXiv:1808.03433](https://arxiv.org/abs/1808.03433).
The journal year is 2019, although the preprint was first submitted in 2018.

(ref-qiu2019)=
**Qiu, Y., Mutch, S. J., da Cunha, E., Poole, G. B. & Wyithe, J. S. B.
(2019).** *Dark-age reionization and galaxy formation simulation – XIX.
Predictions of infrared excess and cosmic star formation rate density from
UV observations.* MNRAS **489**, 1357–1372.
[DOI: 10.1093/mnras/stz2233](https://doi.org/10.1093/mnras/stz2233);
[arXiv:1905.02759](https://arxiv.org/abs/1905.02759).

(ref-davies2019)=
**Davies, J. E., Mutch, S. J., Qin, Y., Mesinger, A., Poole, G. B. & Wyithe,
J. S. B. (2019).** *Dark-ages reionization and galaxy formation simulation –
XVI. The thermal memory of reionization.* MNRAS **489**, 977–992.
[DOI: 10.1093/mnras/stz2241](https://doi.org/10.1093/mnras/stz2241);
[publisher article](https://academic.oup.com/mnras/article/489/1/977/5549525).

(ref-balu2023)=
**Balu, S., Greig, B., Qiu, Y., Power, C., Qin, Y., Mutch, S. & Wyithe,
J. S. B. (2023).** *Thermal and reionization history within a large-volume
semi-analytic galaxy formation simulation.* MNRAS **520**, 3368–3382.
[DOI: 10.1093/mnras/stad281](https://doi.org/10.1093/mnras/stad281);
[arXiv:2210.08910](https://arxiv.org/abs/2210.08910).

(ref-ventura2024)=
**Ventura, E. M., Qin, Y., Balu, S. & Wyithe, J. S. B. (2024).**
*Semi-analytic modelling of Pop. III star formation and metallicity
evolution – I. Impact on the UV luminosity functions at z = 9–16.*
MNRAS **529**, 628–646.
[DOI: 10.1093/mnras/stae567](https://doi.org/10.1093/mnras/stae567);
[arXiv:2401.07396](https://arxiv.org/abs/2401.07396).

## Related Meraxes developments

(ref-marshall2020)=
**Marshall, M. A., Mutch, S. J., Qin, Y., Poole, G. B. & Wyithe, J. S. B.
(2020).** *Dark-ages reionization and galaxy formation simulation – XVIII.
The high-redshift evolution of black holes and their host galaxies.*
MNRAS **494**, 2747–2759.
[DOI: 10.1093/mnras/staa936](https://doi.org/10.1093/mnras/staa936);
[arXiv:1910.08124](https://arxiv.org/abs/1910.08124).

(ref-ventura2025)=
**Ventura, E. M., Qin, Y., Balu, S. & Wyithe, J. S. B. (2025).**
*Semi-analytical modelling of Pop. III star formation and metallicity
evolution – II. Impact on 21 cm power spectrum.* MNRAS **540**, 483–497.
[DOI: 10.1093/mnras/staf699](https://doi.org/10.1093/mnras/staf699);
[publisher article](https://academic.oup.com/mnras/article/540/1/483/8123416).

These papers describe scientific developments beyond the specific feature
set established by the pinned source. Consult their own methods and code
versions when reproducing their results.

## Principal prescription references

### Gas, star formation and feedback

**Sutherland, R. S. & Dopita, M. A. (1993).** *Cooling functions for
low-density astrophysical plasmas.* ApJS **88**, 253–327.
[DOI: 10.1086/191823](https://doi.org/10.1086/191823).
Context for the tabulated atomic cooling coefficients used by Meraxes.

**Croton, D. J., et al. (2006).** *The many lives of active galactic nuclei:
cooling flows, black holes and the luminosities and colours of galaxies.*
MNRAS **365**, 11–28.
[DOI: 10.1111/j.1365-2966.2005.09675.x](https://doi.org/10.1111/j.1365-2966.2005.09675.x);
[author-hosted paper](https://wwwmpa.mpa-garching.mpg.de/mpa/publications/preprints/pp2006/MPA1935.pdf).
Context for the semi-analytic radio-mode feedback framework; the current
Meraxes accretion and heating expressions are given in [Black holes](black-holes.md).

**Blitz, L. & Rosolowsky, E. (2006).** *The Role of Pressure in GMC Formation
II: The H2-Pressure Relation.* ApJ **650**, 933–944.
[DOI: 10.1086/505417](https://doi.org/10.1086/505417);
[arXiv:astro-ph/0605035](https://arxiv.org/abs/astro-ph/0605035).
Context for the pressure-based molecular fraction in the optional
star-formation selector.

**Guo, Q., et al. (2011).** *From dwarf spheroidals to cD galaxies:
simulating the galaxy population in a ΛCDM cosmology.* MNRAS **413**, 101–131.
[DOI: 10.1111/j.1365-2966.2010.18114.x](https://doi.org/10.1111/j.1365-2966.2010.18114.x);
[arXiv:1006.0106](https://arxiv.org/abs/1006.0106).
Context for Guo-type feedback/reincorporation prescriptions.

**Henriques, B. M. B., et al. (2013).** *Simulations of the galaxy population
constrained by observations from z = 3 to the present day: implications for
galactic winds and the fate of their ejecta.* MNRAS **431**, 3373–3395.
[DOI: 10.1093/mnras/stt415](https://doi.org/10.1093/mnras/stt415);
[publisher article](https://academic.oup.com/mnras/article/431/4/3373/1149793).
Context for the halo-mass-dependent reincorporation option.

**Muratov, A. L., Kereš, D., Faucher-Giguère, C.-A., Hopkins, P. F.,
Quataert, E. & Murray, N. (2015).** *Gusty, gaseous flows of FIRE: galactic
winds in cosmological simulations with explicit stellar feedback.*
MNRAS **454**, 2691–2713.
[DOI: 10.1093/mnras/stv2126](https://doi.org/10.1093/mnras/stv2126);
[arXiv:1501.03155](https://arxiv.org/abs/1501.03155).
Context for the velocity/redshift scalings labelled Muratov-type in the
feedback code. This does not make the semi-analytic implementation a FIRE
hydrodynamic calculation.

### AGN spectra and obscuration

**Morrison, R. & McCammon, D. (1983).** *Interstellar photoelectric
absorption cross sections, 0.03–10 keV.* ApJ **270**, 119–122.
[DOI: 10.1086/161102](https://doi.org/10.1086/161102);
[NASA record](https://ntrs.nasa.gov/citations/19830056692).
Reference for the piecewise absorption coefficients in the AGN transmission
calculation.

**Ueda, Y., Akiyama, M., Hasinger, G., Miyaji, T. & Watson, M. G. (2014).**
*Toward the Standard Population Synthesis Model of the X-Ray Background:
Evolution of X-Ray Luminosity and Absorption Functions of Active Galactic
Nuclei Including Compton-Thick Populations.* ApJ **786**, 104.
[DOI: 10.1088/0004-637X/786/2/104](https://doi.org/10.1088/0004-637X/786/2/104);
[arXiv:1402.1836](https://arxiv.org/abs/1402.1836).
Reference for the implemented luminosity/redshift-dependent column-density
distribution.

**Lusso, E., Worseck, G., Hennawi, J. F., Prochaska, J. X., Vignali, C.,
Stern, J. & O'Meara, J. M. (2015).** *The first ultraviolet quasar-stacked
spectrum at z ≃ 2.4 from WFC3.* MNRAS **449**, 4204–4220.
[DOI: 10.1093/mnras/stv516](https://doi.org/10.1093/mnras/stv516);
[arXiv:1503.02075](https://arxiv.org/abs/1503.02075).
Reference for the adopted AGN UV spectral slopes around the Lyman limit.

**Shen, X., Hopkins, P. F., Faucher-Giguère, C.-A., Alexander, D. M.,
Richards, G. T., Ross, N. P. & Hickox, R. C. (2020).** *The bolometric
quasar luminosity function at z = 0–7.* MNRAS **495**, 3252–3275.
[DOI: 10.1093/mnras/staa1381](https://doi.org/10.1093/mnras/staa1381);
[arXiv:2001.02696](https://arxiv.org/abs/2001.02696).
Reference for the UV and soft/hard X-ray bolometric corrections labelled
Shen2020 in the source.

### Reionization, self-shielding and the 21-cm signal

**Mesinger, A., Furlanetto, S. & Cen, R. (2011).** *21cmFAST: a fast,
seminumerical simulation of the high-redshift 21-cm signal.*
MNRAS **411**, 955–972.
[DOI: 10.1111/j.1365-2966.2010.17731.x](https://doi.org/10.1111/j.1365-2966.2010.17731.x);
[arXiv:1003.3878](https://arxiv.org/abs/1003.3878).
Origin of the semi-numerical numerical framework adapted within Meraxes;
installing a current standalone 21cmFAST package does not define this
branch's built-in implementation.

**Sobacchi, E. & Mesinger, A. (2013).** *The depletion of gas in high-redshift
dwarf galaxies from an inhomogeneous reionization.* MNRAS **432**, L51–L55.
[DOI: 10.1093/mnrasl/slt035](https://doi.org/10.1093/mnrasl/slt035);
[arXiv:1301.6776](https://arxiv.org/abs/1301.6776).
Reference for the spatially dependent photoheating critical mass and retained
baryon fraction.

**Rahmati, A., Pawlik, A. H., Raičević, M. & Schaye, J. (2013).** *On the
evolution of the H I column density distribution in cosmological
simulations.* MNRAS **430**, 2427–2445.
[DOI: 10.1093/mnras/stt066](https://doi.org/10.1093/mnras/stt066);
[arXiv:1210.7808](https://arxiv.org/abs/1210.7808).
Reference for the implemented self-shielding attenuation fit.

**Sobacchi, E. & Mesinger, A. (2014).** *Inhomogeneous recombinations during
cosmic reionization.* MNRAS **440**, 1662–1673.
[DOI: 10.1093/mnras/stu377](https://doi.org/10.1093/mnras/stu377);
[arXiv:1402.2298](https://arxiv.org/abs/1402.2298).
Reference for inhomogeneous recombination accounting.

### Stellar populations and dust

**Charlot, S. & Fall, S. M. (2000).** *A Simple Model for the Absorption of
Starlight by Dust in Galaxies.* ApJ **539**, 718–731.
[DOI: 10.1086/309250](https://doi.org/10.1086/309250);
[arXiv:astro-ph/0003128](https://arxiv.org/abs/astro-ph/0003128).
Origin of the age-dependent birth-cloud plus diffuse-ISM attenuation
framework used by the SED/dust development.

**Schaerer, D. (2002).** *On the properties of massive Population III stars
and metal-free stellar populations.* A&A **382**, 28–42.
[DOI: 10.1051/0004-6361:20011619](https://doi.org/10.1051/0004-6361:20011619);
[arXiv:astro-ph/0110697](https://arxiv.org/abs/astro-ph/0110697).
Reference for the Pop. III lifetime fits used by the implemented IMF
integrations.

**Raiter, A., Schaerer, D. & Fosbury, R. A. E. (2010).** *Predicted UV
properties of very metal-poor starburst galaxies.* A&A **523**, A64.
[DOI: 10.1051/0004-6361/201015236](https://doi.org/10.1051/0004-6361/201015236);
[arXiv:1008.2114](https://arxiv.org/abs/1008.2114).
Reference identified by the external Sector repository for its Pop. III
spectral templates; the particular template files remain explicit inputs.
