# Stochasticity setups

This is a starter outline. Add the exact parameter names, defaults and
activation conditions from the branch being documented.

## Source prescriptions

| Setup | Content to document |
|---|---|
| Escape-fraction scatter | Median relation; scatter width; clipping; affected source quantities. |
| noSFR | How the deterministic SFR is constructed; affected source quantities. |
| X-ray scatter | The adopted luminosity–SFR relation and its scatter. |
| Recalibration | Target history; scaling procedure; applicable setup combinations. |
| UVB feedback | How source setups are combined with the selected feedback treatment. |

## Compile-time and runtime controls

Add a table containing each control, its default, activation condition and
source routine. Put a working parameter-file example below the table.

## Equations

The template enables inline mathematics, such as $f_{\rm esc}$, and display
equations:

$$
\log_{10} f_{\rm esc}^{\rm draw}
= \log_{10} f_{\rm esc}^{\rm median}
+ \epsilon, \qquad
\epsilon \sim \mathcal{N}(0,\sigma_{\rm esc}^{2}).
$$

Document clipping and recalibration alongside the prescription.

## Run examples

Add the build commands and parameter files for the setups you want readers
to reproduce.
