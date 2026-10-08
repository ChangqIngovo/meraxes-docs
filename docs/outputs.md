# Outputs

Meraxes saves galaxy catalogues, radiation grids, and global statistics in HDF5 files. Open the master file to access these products through a single hierarchy.

![Output files and snapshot contents](_static/output-tree.svg)

## Files and snapshots

`FileNameGalaxies` sets the filename prefix and `OutputDir` sets the directory. Here, `<p>` is the prefix, `<r>` the MPI rank, and `<s>` the snapshot number.

| File | Contents |
| --- | --- |
| `<p>.hdf5` | Master metadata and links to selected snapshots; assembled by rank 0 after the run. |
| `<p>_<r>.hdf5` | Rank-local galaxy catalogues and merger indices. Rank 0 also holds global distribution functions. |
| `<p>_grids_<s>.hdf5` | Source, ionization, thermal, 21-cm, and optional LW products; written collectively. |
| `<p>_metal_grids_<s>.hdf5` | Metal-enrichment grids when mini-halo and metal-evolution physics are enabled. |

A snapshot is named `SnapNNN`, with a minimum of three digits. Grid filenames use the unpadded snapshot number. The master contains selected output snapshots; intermediate grid files may also hold global summaries. Keep all files together: the master uses relative external links.

| Inside `Snap` | Object | Contents |
| --- | --- | --- |
| `CoreN` | Group | Links to rank N's `Galaxies` and merger-index datasets. |
| `Grids` | External group link | Radiation-grid file, including the `stars` source dataset. |
| `MetalGrids` | External group link | Optional metal-grid file. |
| `HMF`, `SMF`, luminosity functions | External dataset links | Global distributions stored in the rank-0 file. |
| Attributes | Snapshot metadata | `NGalaxies`, `Redshift`, `LTTime`. |

### Metadata and units

| Location | Information |
| --- | --- |
| Root attributes | `NCores`; rank files also store `iCore`. |
| `InputParams` attributes | Effective run parameters, including the determined `EndSnapshotLightcone` when applicable. |
| `Units` attributes | Galaxy-field unit strings. |
| `HubbleConversions` attributes | Galaxy-field h conversions: `v/h`, `v*(h**2)`, `v`, or `None`. |
| `Units/Grids`, `HubbleConversions/Grids` | Grid units and h conversions. |
| `Units/MetalGrids` | Metal-grid units; no separate h-conversion registry. |
| `gitdiff` and its `gitref` attribute | Build revision and source changes, when recorded. |
| `Snap` attributes | `NGalaxies`: total saved rows; `Redshift`: snapshot redshift; `LTTime`: lookback time in Myr/h under the standard units. |

Tables below use the standard simulation units. Masses labelled `10¹⁰ Msun/h` require multiplication by 10¹⁰ and division by `Hubble_h`; `Sfr` is already in Msun/yr. Positions are comoving, while virial and disk radii are physical. Raw `h5py` reads retain all h factors. A dash denotes dimensionless values or identifiers. Numeric attributes are commonly one-element arrays.

### What is saved

| Product | Output condition |
| --- | --- |
| Galaxy catalogue and merger indices | Selected snapshot, ordinary output mode; omitted for `FlagInteractive = 2`. |
| Enabled distributions | Selected snapshot; also available in summary-only mode. |
| Full radiation cubes | `Flag_PatchyReion`, `Flag_OutputGrids`, and an active reionization/output gate. `Flag_OutputGridsPostReion` extends output after reionization. |
| Thermal input/source cubes | Selected thermal-solver outputs; written independently of `Flag_OutputGrids`. |
| Global grid summaries | May be written without cubes, using empty datasets of shape `(0,)` to hold attributes. |

`FlagMCMC` uses a separate output workflow. Check a grid's shape before treating it as a cube; empty attribute holders still contain useful global histories.

## Galaxy catalogues

`Snap/CoreN/Galaxies` is a one-dimensional compound table. Each row represents a galaxy with `Type < 3`, including eligible ghosts and galaxies with zero stellar mass. Indices refer to rows within that rank.

All scalar real fields below are float32; integer fields and array shapes are shown explicitly. `H` denotes `N_HISTORY_SNAPS`, and `B` denotes `MAGS_N_BANDS`. Read their actual lengths from the dataset dtype. The table is chunked and compressed.

### Identity and halo properties

| Field | Type | Meaning | Unit |
| --- | --- | --- | --- |
| `HaloID` | int64 | Host/subhalo identifier; −1 for ghosts. | — |
| `ID` | int64 | Galaxy identifier. | — |
| `Type` | int32 | 0: central; 1: resolved satellite; 2: orphan. | — |
| `CentralGal` | int32 | Rank-local central-galaxy row; −1 for ghosts. | — |
| `GhostFlag` | int32 | Galaxy carried across a missing/skipped halo. | — |
| `Len` | int32 | Current or retained subhalo particle count. | — |
| `MaxLen` | int32 | Largest historical subhalo particle count. | — |
| `Pos` | float32[3] | Comoving position; orphans retain their last resolved position. | cMpc/h |
| `Vel` | float32[3] | Galaxy/halo velocity. | km/s |
| `Spin` | float32 | Halo spin parameter. | — |
| `Mvir` | float32 | Current or retained subhalo virial mass. | 10¹⁰ Msun/h |
| `Rvir` | float32 | Physical virial radius. | Mpc/h |
| `Vvir` | float32 | Virial velocity. | km/s |
| `Vmax` | float32 | Maximum circular velocity. | km/s |
| `FOFMvir` | float32 | Parent FOF mass; −1 for ghosts. | 10¹⁰ Msun/h |
| `FOFMvirModifier` | float32 | FOF-mass correction factor. | — |
| `MergTime` | float32 | Remaining orphan merger time. | Myr/h |
| `MergerStartRadius` | float32 | Initial orbital separation relative to central virial radius. | Ratio; see unit notes below |
| `dt` | float32 | Evolution timestep. | Myr/h |

### Gas and stars

| Field | Type | Meaning | Unit |
| --- | --- | --- | --- |
| `HotGas` | float32 | Hot gas mass. | 10¹⁰ Msun/h |
| `MetalsHotGas` | float32 | Metal mass in hot gas. | 10¹⁰ Msun/h |
| `ColdGas` | float32 | Cold gas mass. | 10¹⁰ Msun/h |
| `MetalsColdGas` | float32 | Metal mass in cold gas. | 10¹⁰ Msun/h |
| `H2Frac` | float32 | Molecular fraction; central fraction in the pressure-law prescription. | — |
| `H2Mass` | float32 | Molecular gas mass. | 10¹⁰ Msun/h |
| `HIMass` | float32 | Atomic gas mass. | 10¹⁰ Msun/h |
| `Mcool` | float32 | Cooling mass accumulated during the snapshot. | 10¹⁰ Msun/h |
| `Rcool` | float32 | Latest cooling radius. | Mpc/h |
| `DiskScaleLength` | float32 | Physical disk scale length. | Mpc/h |
| `EjectedGas` | float32 | Ejected gas awaiting reincorporation. | 10¹⁰ Msun/h |
| `MetalsEjectedGas` | float32 | Metal mass in ejected gas. | 10¹⁰ Msun/h |
| `BaryonFracModifier` | float32 | Suppression factor applied to baryon infall. | — |
| `MvirCrit` | float32 | Local UV-background critical halo mass. | 10¹⁰ Msun/h |
| `StellarMass` | float32 | Surviving stellar mass after recycling. | 10¹⁰ Msun/h |
| `GrossStellarMass` | float32 | Total stellar mass formed before recycling. | 10¹⁰ Msun/h |
| `MetalsStellarMass` | float32 | Stellar metal-mass bookkeeping. | 10¹⁰ Msun/h |
| `Sfr` | float32 | Snapshot star-formation rate. | Msun/yr |
| `NewStars` | float32[H] | Formed stellar mass per snapshot; index 0 is most recent. | 10¹⁰ Msun/h |
| `MergerBurstMass` | float32 | Cumulative mass formed in merger bursts. | 10¹⁰ Msun/h |
| `MWMSA` | float32 | Mass-weighted mean stellar age. | See unit notes below |
| `Fesc` | float32 | Untreated stellar ionizing escape fraction. | — |
| `FescWeightedSfr` | float32 | Untreated escape-weighted stellar SFR. | Msun/yr |
| `FescWeightedGSM` | float32 | Cumulative untreated escape-weighted formed stellar mass. | 10¹⁰ Msun/h |
| `tau_cgm` | float32 | CGM optical-depth term for escape suppression. | — |
| `Cos_Inc` | float32 | Cosine of disk inclination used for attenuation. | — |
| `LOIII` | float32 | Intrinsic [O III] luminosity. | 10⁴⁰ erg/s |
| `ionization_param` | float32 | Line-emission parameter q. | cm/s |

`Metals*` fields contain metal masses, rather than metallicity ratios. `Fesc`, `FescWeightedSfr`, and `FescWeightedGSM` retain untreated values; stochastic source grids use separate accumulators and may be recalibrated during [source deposition](workflow.md#radiation-and-feedback).

### Black holes and AGN

| Field | Type | Meaning | Unit |
| --- | --- | --- | --- |
| `BlackHoleMass` | float32 | Black-hole mass. | 10¹⁰ Msun/h |
| `BlackHoleAccretedHotMass` | float32 | Snapshot hot-mode accreted mass. | 10¹⁰ Msun/h |
| `BlackHoleAccretedColdMass` | float32 | Snapshot cold-mode accreted mass. | 10¹⁰ Msun/h |
| `FescBH` | float32 | AGN ionizing escape fraction. | — |
| `BHemissivity` | float32 | Effective AGN ionizing source rate. | See unit notes below |
| `EffectiveBHM` | float32 | Cumulative AGN budget in equivalent stellar-source mass. | 10¹⁰ Msun/h |
| `QuasarMag` | float32 | Intrinsic absolute magnitude at 1450 Å; 999.9 if no UV luminosity. | AB mag |
| `QuasarLX` | float32 | Intrinsic 2–10 keV luminosity. | 10¹⁰ Lsun |
| `BHXrayEmissivity` | float32 | Obscured/observed 2–10 keV luminosity. | 10¹⁰ Lsun |
| `NHbin` | int32 | Column-density bin 0–4: log NH intervals 20–21, 21–22, 22–23, 23–24, 24–26; −1: no AGN. | Index; NH in cm⁻² |
| `DutyCycleAGN` | float32 | AGN active fraction, bounded between 0 and 1. | — |

### Optional galaxy fields

The following 15 fields require `USE_MINI_HALOS`.

| Field | Type | Meaning | Unit |
| --- | --- | --- | --- |
| `Galaxy_Population` | int32 | Population: 2 for Pop II; 3 for Pop III. | — |
| `Flag_ExtMetEnr` | int32 | External enrichment flag. | — |
| `Pop2StellarMass` | float32 | Surviving Pop II stellar mass. | 10¹⁰ Msun/h |
| `Pop3StellarMass` | float32 | Surviving Pop III stellar mass. | 10¹⁰ Msun/h |
| `RemnantMass` | float32 | Stellar remnant mass. | 10¹⁰ Msun/h |
| `GrossStellarMassIII` | float32 | Cumulative formed Pop III mass. | 10¹⁰ Msun/h |
| `FescIIIWeightedSfr` | float32 | Untreated escape-weighted Pop III SFR. | Msun/yr |
| `RmetalBubble` | float32 | Physical metal-bubble radius. | Mpc/h |
| `MetalProbability` | float32 | Local grid enrichment probability. | — |
| `GalMetalProbability` | float32 | Per-galaxy random variate compared with enrichment probability. | [0, 1) |
| `MvirCrit_MC` | float32 | Molecular-cooling critical mass. | 10¹⁰ Msun/h |
| `NewStarsPop2` | float32[H] | Pop II formation history, newest first. | 10¹⁰ Msun/h |
| `NewStarsPop3` | float32[H] | Pop III formation history, newest first. | 10¹⁰ Msun/h |
| `FescIII` | float32 | Untreated Pop III escape fraction. | — |
| `FescIIIWeightedGSM` | float32 | Cumulative untreated escape-weighted Pop III formed mass. | 10¹⁰ Msun/h |

`CALC_MAGS` adds photometry at configured target snapshots, in the configured band order.

| Field | Type | Meaning | Unit |
| --- | --- | --- | --- |
| `LOIII_dusty` | float32 | Attenuated [O III] luminosity; initially intrinsic if no suitable rest-band attenuation exists. | 10⁴⁰ erg/s |
| `Mags` | float32[B] | Intrinsic magnitudes. | mag |
| `DustyMags` | float32[B] | Dust-attenuated magnitudes. | mag |
| `MagsIII` | float32[B] | Pop III magnitudes; also requires `USE_MINI_HALOS`. | mag |

### Unit notes

| Field | Reading convention |
| --- | --- |
| `MergerStartRadius` | Stored dimensionless radius ratio; ignore its legacy `Mpc`, `v/h` metadata. |
| `MWMSA` | Stored in internal time units despite `Myr` metadata; apply the run's time-unit conversion before removing h. |
| `BHemissivity` | Effective rate after equivalent-mass, duty-cycle, and response treatment; the legacy `1e60 photons` label does not describe a photon count. |

### Merger indices

| Dataset under `CoreN` | Length | Meaning |
| --- | --- | --- |
| `FirstProgenitorIndices` | Current galaxy count | First progenitor's row in the preceding snapshot. |
| `DescendantIndices` | Previous galaxy count | Descendant's row in the following snapshot. |
| `NextProgenitorIndices` | Previous galaxy count | Next row in the progenitor list sharing a descendant. |

These integer arrays use rank-local rows, with −1 for missing connections. Links are generated only for adjacent simulation snapshots that are both saved. The latter two arrays are added retrospectively to the earlier snapshot; the final output normally lacks them. Preserve rank offsets when concatenating catalogues.

## Radiation grids

A full field is a float32 cube with `ReionGridDim` cells per axis. Cubes are uncompressed, chunked by x plane, and occupy four bytes per cell. Lightcones, power spectra, and spectral diagnostics have the alternative shapes listed below.

| Abbreviation | Configuration |
| --- | --- |
| BH | `physics.Flag_BHFeedback` |
| Rec | `Flag_IncludeRecombinations` |
| UVB | `ReionUVBFlag` enabled |
| Spin | `Flag_IncludeSpinTemp` |
| Bright | `Flag_Compute21cmBrightTemp` |
| LC / PS | `Flag_ConstructLightcone` / `Flag_ComputePS` |
| Mini / LW | `USE_MINI_HALOS` / `Flag_IncludeLymanWerner` |

Conditions below apply within the output gates listed above. **`stars` is a saved grid dataset:** each cell sums the cumulative escape-weighted formed stellar mass deposited by galaxies. It is produced during source-grid construction, alongside rate grids, and supplies the ionization calculation.

### Source grids

| Dataset | Meaning | Additional condition | Unit |
| --- | --- | --- | --- |
| `deltax` | Simulation density contrast. | Source writer | — |
| `stars` | Cell sum of untreated or stochastic cumulative escaped stellar-source mass, including enabled recalibration. | Source writer | 10¹⁰ Msun/h |
| `weighted_sfr` | Cell sum of escape-weighted stellar SFR. | Source writer | Msun/yr |
| `effective_bhm` | Cumulative AGN budget in equivalent stellar-source mass; only BHs above `BlackHoleMassLimitReion`. | Source writer + BH | 10¹⁰ Msun/h; unregistered |
| `effective_bhar` | Equivalent AGN source rate with the same mass selection. | Source writer + BH | Msun/yr |
| `sfr` | Unweighted thermal source rate from the configured SFR or mass/timescale prescription. | Source writer + Spin | Msun/yr; unregistered |

Stochastic X-ray luminosity and AGN hard/soft source arrays are not saved as full cubes; `sfr` does not contain their luminosity draws.

### Ionization, temperature, and 21-cm products

| Dataset | Meaning | Additional condition | Unit |
| --- | --- | --- | --- |
| `xH` | Neutral hydrogen fraction. | Full-grid writer | — |
| `r_bubble` | Ionized-bubble/filter radius; populated by the recombination treatment. | Full-grid writer | cMpc/h |
| `temp_kinetic_all_gas` | Temperature diagnostic combining neutral and ionized gas. | Full-grid writer | K |
| `z_at_ionization` | Redshift of first full cell ionization. | Rec | — |
| `residual_xH` | Scaled subgrid residual neutral fraction. | Rec | Stored at 10⁴ times its unscaled value |
| `clumping_factor` | Ionized-gas clumping factor. | Rec | — |
| `Gamma12` | Photoionization rate diagnostic. | Rec | 10⁻¹² s⁻¹; multiply by h² |
| `t_resp` | Ionization-response timescale. | Rec | Myr |
| `N_rec` | Cumulative recombinations per baryon. | Rec | — |
| `J_21_at_ionization` | UV intensity retained at ionization and updated according to UVB mode. | UVB | 10⁻²¹ erg/s/Hz/cm²/sr; multiply by h² |
| `Mvir_crit` | UVB suppression mass, sampled for subsequent galaxy evolution. | UVB | 10¹⁰ Msun/h |
| `TS_box` | Hydrogen spin temperature. | Spin | K |
| `Tk_box` | Kinetic temperature from the thermal solver. | Spin | K |
| `x_e_box` | Partial-ionization electron fraction, written from `x_e_box_prev`. | Spin | — |
| `delta_T` | Coeval differential 21-cm brightness. | Bright | mK |
| `LightconeBox` | Interpolated brightness; shape `(D, D, LightconeLength)`. | LC; final lightcone snapshot, excluding snapshot 0 | mK |
| `lightcone-z` | Redshift per lightcone slice; length `LightconeLength`. | Same as `LightconeBox` | —; unregistered |
| `k_bins` | Mean wavenumber per bin; length `PS_Length`. | PS | cMpc⁻¹; unregistered |
| `PS_data` | Dimensional 21-cm power per logarithmic wavenumber interval; length `PS_Length`. | PS | mK² |
| `PS_error` | Fourier-mode-count uncertainty; length `PS_Length`. | PS | mK² |

`x_e_box` includes partial ionization and is not the complement of `xH`. The power normalization is given in [Formulas](formulas/igm.md).

### Mini-halo and LW products

All fields below require Mini. The `II` channel omits Pop III thermal/radiation sources but retains AGN contributions and uses the model's ionization field.

| Dataset | Meaning | Additional condition | Unit |
| --- | --- | --- | --- |
| `starsIII` | Cell sum of cumulative escaped Pop III source mass. | Source writer | 10¹⁰ Msun/h |
| `weighted_sfrIII` | Cell sum of escaped Pop III SFR. | Source writer | Msun/yr |
| `sfrIII` | Unweighted Pop III thermal source rate. | Source writer + Spin | Msun/yr; unregistered |
| `Mvir_crit_MC` | LW molecular-cooling critical mass. | UVB + LW | 10¹⁰ Msun/h |
| `JLW_box` | Total LW intensity from stars and AGN. | LW | 10⁻²¹ erg/s/Hz/cm²/sr |
| `JLW_boxII` | LW intensity without Pop III. | LW | Same as `JLW_box` |
| `TS_boxII` | Spin temperature without Pop III heating/coupling. | Spin | K |
| `Tk_boxII` | Kinetic temperature for that channel. | Spin | K |
| `delta_TII` | Brightness for that channel. | Bright | mK |
| `PSII_data` | Power of `delta_TII`; length `PS_Length`. | PS | mK² |
| `PSII_error` | Corresponding mode-count uncertainty. | PS | mK² |

Mini + Spin + LW also produces float64 shell/spectral arrays. Here `F` denotes `TsNumFilterSteps`, and `Q` denotes `LW_NLEV`. Their normalization belongs to the LW emissivity calculation; no unit registry is supplied.

| Dataset | Shape | Meaning |
| --- | --- | --- |
| `LW_shape_stellar` | `(F,)` | Ordinary-stellar spectral/survival factor per shell. |
| `LW_shape_III` | `(F,)` | Pop III factor. |
| `LW_shape_AGN` | `(F,)` | AGN factor. |
| `LW_zpp` | `(F,)` | Source-emission redshift per shell. |
| `LW_emissivity_stellar` | `(F,)` | Shell-dependent mean ordinary-stellar emissivity factor. |
| `LW_emissivity_III` | `(F,)` | Pop III emissivity factor. |
| `LW_emissivity_AGN` | `(F,)` | AGN factor, including its LW efficiency. |
| `LW_spectral_stellar` | `(F, Q)` | Ordinary-stellar contributions per Lyman level. |
| `LW_spectral_III` | `(F, Q)` | Pop III contributions per level. |
| `LW_spectral_AGN` | `(F, Q)` | AGN contributions per level. |

The spectral axis is indexed by Lyman level, beginning at level 2. `LightconeBoxII` is not written.

### Grid unit conventions

| Dataset | Metadata detail |
| --- | --- |
| `TS_box`, `TS_boxII` | Unit keys are spelled `Ts_box`, `Ts_boxII`. |
| `JLW_boxII` | Unit key is `JLW_box_II`. |
| `starsIII`, `weighted_sfrIII` | Unit entries are created only with LW enabled. |
| `J_21_at_ionization` | Legacy unit text says `10e-21`; the calculation uses the 10⁻²¹ intensity normalization. |
| `residual_xH` | Multiply by 10⁻⁴ to remove the stored scaling; this remains a subgrid diagnostic. |

## Global grid attributes

Attributes store box-wide summaries without requiring a full cube read. Each is a one-element float64 value attached to the dataset named in the first column. Volume weighting averages cells; mass weighting weights them by density. Attributes retain the calculation's normalization.

### Ionization and source summaries

| Dataset | Attribute names | Meaning |
| --- | --- | --- |
| `xH` | `volume_weighted_global_xH`, `mass_weighted_global_xH` | Global neutral fractions. |
| `xH` | `mass_weighted_global_tau_e`, `mass_weighted_global_tau_e_sim` | Thomson optical depth; `_sim` contains the simulated history, while the total adds the fully ionized low-redshift contribution. |
| `r_bubble` | `volume_weighted_global_r_bubble`, `mass_weighted_global_r_bubble` | Mean bubble/filter radius. |
| `temp_kinetic_all_gas` | `volume_weighted_global_temp_kinetic_all_gas`, `mass_weighted_global_temp_kinetic_all_gas` | Mean all-gas temperature, K. |
| `Gamma12` | `volume_weighted_global_Gamma12`, `mass_weighted_global_Gamma12` | Mean photoionization rate; Rec. |
| `N_rec` | `volume_weighted_global_N_rec`, `mass_weighted_global_N_rec` | Mean recombinations per baryon; Rec. |
| `residual_xH` | `volume_weighted_global_residual_xH`, `mass_weighted_global_residual_xH` | Mean scaled residual fraction; Rec. |
| `clumping_factor` | `volume_weighted_global_clumping_factor`, `mass_weighted_global_clumping_factor` | Mean clumping factor; Rec. |
| `weighted_sfr` | `volume_weighted_global_weighted_sfr` | Mean escaped stellar SFR per cell, Msun/yr. |
| `effective_bhar` | `volume_weighted_global_effective_bhar` | Mean equivalent AGN source rate per cell, Msun/yr; BH. |
| `weighted_sfrIII` | `volume_weighted_global_weighted_sfrIII` | Mean escaped Pop III SFR per cell, Msun/yr; Mini. |

For a rate density, divide a per-cell source average by cell volume. The low-redshift optical-depth term extends to the last requested snapshot, with doubly ionized helium below redshift 4 and singly ionized helium above it.

### Thermal and brightness summaries

| Dataset | Attribute | Meaning / unit | Condition |
| --- | --- | --- | --- |
| `TS_box` | `volume_ave_TS` | Mean spin temperature, K. | Spin |
| `Tk_box` | `volume_ave_TK` | Mean kinetic temperature, K. | Spin |
| `x_e_box` | `volume_ave_xe` | Mean partial-ionization electron fraction. | Spin |
| `TS_box` | `volume_ave_J_alpha` | Mean Lyα photon-number specific intensity. | Spin |
| `TS_box` | `volume_ave_xalpha` | Mean Wouthuysen–Field coupling with spectral correction. | Spin |
| `TS_box` | `volume_ave_Xheat` | X-ray temperature derivative per redshift, K. | Spin |
| `TS_box` | `volume_ave_Xion` | X-ray source contribution to electron-fraction derivative per redshift. | Spin |
| `TS_box` | `volume_ave_Xheat_AGN_soft` | Soft-AGN temperature derivative per redshift, K. | Spin |
| `TS_box` | `volume_ave_Xheat_AGN_hard` | Hard-AGN temperature derivative per redshift, K. | Spin |
| `delta_T` | `volume_ave_Tb` | Mean coeval brightness, mK. | Bright |
| `TS_boxII` | `volume_ave_TSII` | Mean spin temperature without Pop III sources, K. | Mini + Spin |
| `Tk_boxII` | `volume_ave_TKII` | Mean kinetic temperature for that channel, K. | Mini + Spin |
| `TS_boxII` | `volume_ave_J_alphaII` | Mean Lyα number intensity for that channel. | Mini + Spin |
| `TS_boxII` | `volume_ave_XheatII` | X-ray temperature derivative for that channel, K per redshift. | Mini + Spin |
| `TS_boxII` | `volume_ave_XionII` | X-ray source electron-fraction derivative for that channel, per redshift. | Mini + Spin |
| `JLW_box` | `volume_ave_JLW` | Mean total LW intensity. | Mini + LW |
| `JLW_boxII` | `volume_ave_JLW_II` | Mean LW intensity without Pop III. | Mini + LW |
| `JLW_box` | `volume_ave_JLW_AGN` | Mean AGN LW intensity. | Mini + LW |
| `delta_TII` | `volume_ave_TbII` | Mean brightness without Pop III thermal/radiation sources, mK. | Mini + Bright |

`Xheat` excludes adiabatic, Compton, and changing-species terms; `Xion` excludes recombination. Positive heating or ionization gives a negative redshift derivative because time increases as redshift decreases. Storage on `TS_box` groups these summaries together; each attribute retains its own physical meaning.

## Metal grids

`Snap/MetalGrids` requires Mini and `Flag_IncludeMetalEvo`. Fields are float32 cubes with `MetalGridDim` cells per axis, uncompressed and chunked by x plane.

| Dataset | Meaning | Standard stored unit |
| --- | --- | --- |
| `Probability_metals` | Metal-pollution probability/filling factor, bounded between 0 and 1. | — |
| `Average Radius` | Mean comoving bubble radius for contributing sources. | cMpc/h; registry key `R_ave` |
| `Max Radius` | Sum over rank-local maximum source-bubble radii. | cMpc/h; registry key `R_max` |
| `mass_IGM` | Density-derived cell baryon mass plus the nonnegative gas correction. | Msun/h |
| `N_bubbles` | Number of positive-radius source bubbles assigned to the cell. | Count stored as float32 |
| `mass_metals` | Ejected metal mass from IGM-polluting bubbles. | Msun/h |
| `mass_gas` | Nonnegative correction from ejected gas minus retained hot and cold gas. | Msun/h |

IGM-polluting bubbles must extend to at least three virial radii. `Max Radius` combines rank-local maxima by summation, so it is not an exact global maximum. Metal mass/radius metadata omits the retained h factor. `Zigm_box` appears in the unit registry but is not written as a dataset.

## Mass and luminosity functions

Each distribution is linked directly under `Snap`. It is a float64 array with three columns: **bin center, number density, uncertainty**. Attributes are `n_bins`, `x_min`, `x_max`, `bin_width`, `volume`, `description`, `units`, and `columns` (stored as `center,density,uncertainty`).

| Dataset | Configuration | Coordinate and selection | Density unit |
| --- | --- | --- | --- |
| `HMF` | `Flag_OutputHMF` | Log host/subhalo virial mass in Msun; excludes ghosts. | cMpc⁻³ dex⁻¹ |
| `SMF` | `Flag_OutputSMF` | Log positive stellar mass in Msun; excludes ghosts. | cMpc⁻³ dex⁻¹ |
| `UVLF` | `CALC_MAGS`, `Flag_OutputUVLF` | Finite intrinsic magnitude in band 0; excludes ghosts. | cMpc⁻³ mag⁻¹ |
| `DustyLF` | `CALC_MAGS`, `Flag_OutputDustyLF` | Finite attenuated magnitude in band 0; excludes ghosts. | cMpc⁻³ mag⁻¹ |
| `OIIILF` | `Flag_OutputOIIILF` | Log positive intrinsic [O III] luminosity in erg/s; excludes ghosts. | cMpc⁻³ dex⁻¹ |
| `OIIIDustyLF` | `CALC_MAGS`, `Flag_OutputOIIILF` | Log positive attenuated [O III] luminosity; requires rest-band attenuation; excludes ghosts. | cMpc⁻³ dex⁻¹ |
| `QuasarLF` | `Flag_OutputQuasarLF` | Finite UV magnitude below 900; duty-cycle and visibility weighting; excludes ghosts. | cMpc⁻³ mag⁻¹ |
| `XrayLF` | `Flag_OutputXrayLF` | Log positive intrinsic 2–10 keV luminosity in erg/s; duty-cycle weighting. | cMpc⁻³ dex⁻¹ |
| `XrayLF_obs` | `Flag_OutputXrayLF` | Obscured 2–10 keV luminosity with the same weighting. | cMpc⁻³ dex⁻¹ |

Photometric distributions require a target photometry snapshot. X-ray distributions do not exclude ghosts separately. Bin parameters are listed in [Inputs](inputs.md); use the stored centers and widths for analysis. Uncertainties use Bernoulli statistics for activity-weighted distributions with nonzero variance, and Poisson counts otherwise. See [Formulas](formulas/numerics.md) for binning and normalization.

### X-ray diagnostics

`Flag_OutputXrayLF` also writes these root-level float64 datasets. The emissivity histories require Spin and are indexed by simulation snapshot number.

| Dataset | Shape | Meaning |
| --- | --- | --- |
| `NHTrans` | `(5,)` | Hard-X-ray transmission in each obscuring column-density bin. |
| `NHfrac` | `(n_lx_bins, 5)` | Expected bin fractions at the X-ray luminosity centers, evaluated at redshift 2. |
| `XrayEmissivity_hard` | `(SnaplistLength,)` | Mean hard-AGN heating-source luminosity density. |
| `XrayEmissivity_soft` | `(SnaplistLength,)` | Mean soft-AGN heating-source luminosity density. |
| `XrayEmissivity_HMXB` | `(SnaplistLength,)` | Mean stellar/HMXB heating-source luminosity density. |

Histories use erg/s/cm³ in the internal length normalization, retaining its h convention. Uncomputed entries remain zero. No dedicated unit metadata is attached; `NHfrac` is a model expectation rather than a measured galaxy histogram.

## Reading data

Read metadata first, then select catalogue fields and grid slices. This example uses the latest available snapshot and the first rank catalogue.

```python
import h5py

with h5py.File("output/meraxes.hdf5", "r") as f:
    names = sorted((n for n in f if n.startswith("Snap")),
                   key=lambda n: int(n[4:]))
    snap = f[names[-1]]
    print(dict(snap.attrs), list(snap))
    print(dict(f["Units"].attrs))
    print(dict(f["HubbleConversions"].attrs))

    cores = sorted((n for n in snap if n.startswith("Core")),
                   key=lambda n: int(n[4:]))
    if cores and "Galaxies" in snap[cores[0]]:
        galaxies = snap[cores[0]]["Galaxies"]
        print(galaxies.shape, galaxies.dtype.names)
        block = galaxies.fields(["ID", "StellarMass", "Sfr"])[:100_000]

    if "Grids" in snap:
        print(snap.get("Grids", getlink=True))
        xh = snap["Grids/xH"]
        print(xh.shape, dict(xh.attrs))
        if xh.ndim == 3:
            plane = xh[xh.shape[0] // 2, :, :]
```

For convenience readers and analysis examples, see the [DRAGONS documentation](https://meraxes-devs.github.io/dragons/). `h5py` is useful for selected fields, slices, and block reads; DRAGONS provides catalogue concatenation and supported h conversions.
