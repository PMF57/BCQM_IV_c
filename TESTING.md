# TESTING — BCQM IV_c Soft-Rudder Single-Thread Inertial Noise

This file documents the basic numerical checks for the **bcqm_soft_rudder** code
that accompanies

> *Boundary-Condition Quantum Mechanics IV_c:  
> Diffusive inertia and the limits of binary hop kernels*.

The goal is to ensure that a fresh checkout of the repository can reproduce
the reference inertial-noise scaling result
\(A(W_{\mathrm{coh}}) \sim W_{\mathrm{coh}}^{-\beta}\) with
\(\beta \approx 0.5\) for the soft-rudder single-thread kernel.

---

## 1. Environment

The reference tests were run with:

- Python 3.10 (CPython)
- NumPy 1.26.x
- SciPy 1.13.x
- PyYAML 6.x
- Matplotlib 3.8.x (only needed for plotting)

All tests assume a standard 64-bit CPU and should run comfortably on a laptop.

---

## 2. Reference W_coh scan

### 2.1 Configuration

The main validation run uses the YAML configuration:

```yaml
simulation:
  dt: 1.0
  n_steps: 16384
  n_ensembles: 64
  seed: 12345

scan:
  wcoh_values: [5.0, 10.0, 20.0, 40.0, 80.0, 160.0]
  label: soft_rudder_wcoh_scan
```

- `dt` — time step (fixed to 1.0 in the IV_c paper).
- `n_steps` — number of steps per trajectory.
- `n_ensembles` — number of trajectories in the ensemble.
- `seed` — random seed for reproducibility.
- `wcoh_values` — list of coherence-horizon values scanned.
- `label` — used to construct the output filenames.

### 2.2 Running the scan

From the repository root:

```bash
python3 -m bcqm_soft_rudder.cli run configs/wcoh_scan_soft_rudder.yml
```

Expected console output (up to small floating-point variations):

```text
Scanning W_coh values: [  5.  10.  20.  40.  80. 160.]
W_coh = 5:   A = 0.0248, omega_c = 2.08
W_coh = 10:  A = 0.0175, omega_c = 1.84
W_coh = 20:  A = 0.0124, omega_c = 1.71
W_coh = 40:  A = 0.0087, omega_c = 1.64
W_coh = 80:  A = 0.0062, omega_c = 1.61
W_coh = 160: A = 0.0044, omega_c = 1.59
```

This run produces:

- `outputs_soft_rudder/amplitude_scaling_soft_rudder.csv`
- `outputs_soft_rudder/Wcoh_*.npz` files (ensemble PSD data).

### 2.3 Fitting beta

To fit the exponent \(\beta\) from the CSV file:

```bash
python3 -m bcqm_soft_rudder.fit_beta outputs_soft_rudder/amplitude_scaling_soft_rudder.csv
```

Expected output:

```text
Fitted beta (A ~ W^(-beta)): beta ≈ 0.50
```

Typical reference result:

- \(\beta = 0.499 \pm \mathcal{O}(10^{-3})\)

This is the diffusive single-thread exponent reported in BCQM IV_c.

---

## 3. Convergence checks

This section records basic convergence checks performed on the reference model.

### 3.1 Steps per trajectory (n_steps)

We varied `n_steps` while keeping all other parameters fixed:

- `n_steps = 8192`
- `n_steps = 16384` (reference)
- `n_steps = 32768`

Observed behaviour:

- Increasing `n_steps` improves the smoothness of the PSD and slightly reduces
  the scatter in the fitted \(\beta\).
- The central value of \(\beta\) remains stable within ~0.01 across this range.

Conclusion: `n_steps = 16384` is a reasonable compromise between accuracy and runtime.

### 3.2 Ensemble size (n_ensembles)

We varied `n_ensembles` with fixed `n_steps = 16384`:

- `n_ensembles = 32`
- `n_ensembles = 64` (reference)
- `n_ensembles = 128`

Observed behaviour:

- Larger ensembles reduce fluctuations in the estimated amplitudes and hence
  tighten the uncertainty on \(\beta\).
- The central value of \(\beta\) remains consistent within statistical error.

Conclusion: `n_ensembles = 64` is sufficient for the purposes of BCQM IV_c.
Larger values are optional for more precise error bars.

---

## 4. Sensitivity to slip prefactor k

The soft-rudder kernel uses a slip law of the form

\[
q(W_{\mathrm{coh}}) = 1 - p_{\mathrm{stay}}(W_{\mathrm{coh}}) = \frac{k}{W_{\mathrm{coh}}},
\]

with a reference prefactor \(k = 2.0\).

We verified that:

- Changing `k` rescales the overall amplitude \(A(W_{\mathrm{coh}})\), as expected,
- but does **not** change the exponent \(\beta\) within numerical error.

For example:

- `k = 1.0` → \(\beta \approx 0.50\)
- `k = 2.0` → \(\beta \approx 0.50\) (reference)
- `k = 4.0` → \(\beta \approx 0.50\)

Conclusion: \(\beta \approx 1/2\) is robust to moderate changes in the slip prefactor.

---

## 5. Telegrapher scaling sanity check

The single-thread binary model is a discrete analogue of telegraph noise:
the direction flips with probability \(q(W_{\mathrm{coh}})\) on each step.

Analytical considerations for telegraph processes suggest a scaling relation

\[
\beta \approx \frac{\alpha}{2}
\]

for slip laws of the form

\[
q(W_{\mathrm{coh}}) \propto W_{\mathrm{coh}}^{-\alpha}.
\]

We verified this numerically by:

- modifying the code to allow general \(\alpha\),
- scanning \(W_{\mathrm{coh}}\) for \(\alpha = 1\) and \(\alpha = 3\),
- fitting \(\beta\) in each case.

Results (illustrative):

- \(\alpha = 1\) → \(\beta \approx 0.5\) (diffusive)
- \(\alpha = 3\) → \(\beta \approx 1.5\)

This is consistent with the telegraph scaling \(\beta \approx \alpha/2\), and
supports the interpretation that the soft-rudder kernel falls in the
diffusive universality class for the natural choice \(\alpha = 1\).

---

## 6. Re-running and extending the tests

If you change the kernel or the YAML configuration, we recommend:

1. Re-running the reference `wcoh_scan_soft_rudder.yml` to check that the pipeline
   (PSD estimation + amplitude extraction + \(\beta\) fit) still behaves as expected.
2. Adding a brief note here describing:
   - the modified configuration,
   - the new \(\beta\) value,
   - and any observed differences.

This helps keep the code and the BCQM IV_c paper tightly aligned and makes it
easier for others to reproduce and extend the results.

