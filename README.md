# BCQM IV_c — Soft-Rudder Single-Thread Inertial Noise

This repository contains the reference implementation for

> **Boundary-Condition Quantum Mechanics IV_c:  
> Diffusive inertia and the limits of binary hop kernels**

It implements the **single-thread, binary soft-rudder model** used in BCQM IV_c to show that, for natural slip laws,
the inertial-noise amplitude scales with the coherence horizon as
\[
A(W_{\mathrm{coh}}) \sim W_{\mathrm{coh}}^{-\beta}, \qquad \beta \approx \tfrac{1}{2},
\]
i.e. single primitive threads live in a **diffusive** universality class.

The code reproduces the numerical results and plots in the paper:
- the **amplitude vs. \(W_{\mathrm{coh}}\)** scaling,
- the fitted exponent **\(\beta \approx 0.5\)** for the soft-rudder kernel.

---

## Repository layout

```text
bcqm_soft_rudder/
    __init__.py
    model.py          # soft-rudder kernel and trajectory generator
    spectra.py        # PSD estimation and amplitude extraction
    cli.py            # command-line interface for scans
    fit_beta.py       # standalone beta-fit helper

configs/
    wcoh_scan_soft_rudder.yml  # reference W_coh scan configuration

outputs_soft_rudder/
    (created on first run)
    amplitude_scaling_soft_rudder.csv
    Wcoh_5.npz
    Wcoh_10.npz
    ...
    Wcoh_160.npz

README.md
TESTING.md                # numerical checks and validation notes
pyproject.toml / setup.cfg (if present)
```

---

## Dependencies

Tested with:

- Python 3.10+  
- `numpy`  
- `scipy`  
- `pyyaml`  
- `matplotlib` (only needed if you want to make plots yourself)

You can install everything into a local virtual environment, for example:

```bash
python3 -m venv .venv
source .venv/bin/activate  # on macOS / Linux
# .venv\Scripts\activate   # on Windows (PowerShell / cmd)

pip install -r requirements.txt
# or, if using pyproject.toml:
# pip install .
```

---

## Quick start: reproduce the reference W_coh scan

From the repository root:

```bash
source .venv/bin/activate    # if using a virtual environment

python3 -m bcqm_soft_rudder.cli run configs/wcoh_scan_soft_rudder.yml
```

You should see output similar to:

```text
Scanning W_coh values: [  5.  10.  20.  40.  80. 160.]
W_coh = 5:   A = 0.02478, omega_c = 2.08
W_coh = 10:  A = 0.01754, omega_c = 1.84
W_coh = 20:  A = 0.01235, omega_c = 1.71
W_coh = 40:  A = 0.00873, omega_c = 1.64
W_coh = 80:  A = 0.00620, omega_c = 1.61
W_coh = 160: A = 0.00440, omega_c = 1.59
```

This run will create:

- `outputs_soft_rudder/amplitude_scaling_soft_rudder.csv`  
- `outputs_soft_rudder/Wcoh_*.npz` (ensemble PSD data for each \(W_{\mathrm{coh}}\))

To fit the exponent \(\beta\) from the CSV file:

```bash
python3 -m bcqm_soft_rudder.fit_beta outputs_soft_rudder/amplitude_scaling_soft_rudder.csv
```

Expected output (up to statistical fluctuations):

```text
Fitted beta (A ~ W^(-beta)): beta = 0.499
```

which is the **diffusive** scaling reported in BCQM IV_c.

---

## Configuration file

The scan is controlled by a simple YAML file, e.g.:

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

- `dt` — time step (fixed to 1.0 in the IV_c paper; kept configurable for convenience).
- `n_steps` — number of time steps per trajectory; higher values improve spectral resolution at the cost of CPU time.
- `n_ensembles` — number of independent trajectories in the ensemble; higher values reduce statistical noise.
- `seed` — random seed for reproducibility.
- `wcoh_values` — list of \(W_{\mathrm{coh}}\) values to scan.
- `label` — used to tag output files in `outputs_soft_rudder/`.

You can create additional config files (e.g. to test different \(W_{\mathrm{coh}}\) ranges
or ensemble sizes) and pass them to the CLI in the same way.

---

## Model details (soft-rudder kernel)

The core of the model (in `bcqm_soft_rudder/model.py`) is:

- A single **binary velocity** thread \(v_n \in \{+1, -1\}\).
- A fixed-step **position** update \(x_{n+1} = x_n + v_n\).
- A **slip law**:
  \[
    q(W_{\mathrm{coh}}) = 1 - p_{\mathrm{stay}}(W_{\mathrm{coh}}) = \frac{k}{W_{\mathrm{coh}}},
  \]
  with \(k = 2.0\), so that the direction flips with probability \(q(W_{\mathrm{coh}})\) on each tick.

Acceleration is defined as the second difference,
\[
  a_n = x_{n+1} - 2 x_n + x_{n-1},
\]
and the **acceleration power spectral density** is estimated via Welch’s method (see `spectra.py`). The amplitude
\[
  A(W_{\mathrm{coh}}) = \sqrt{\int_0^\infty S_a(\omega)\, d\omega}
\]
is obtained by integrating the ensemble-averaged PSD.

The pipeline is identical to that used in the BCQM IV_b control model, so the two codes can be compared directly.

---

## Output files

A typical run generates:

- `outputs_soft_rudder/amplitude_scaling_soft_rudder.csv`  

  CSV with columns:

  ```text
  Wcoh, A, omega_c
  5.0, 0.02478188, 2.08026
  10.0, 0.01753947, 1.83590
  ...
  ```

- `outputs_soft_rudder/Wcoh_XX.npz`  

  For each \(W_{\mathrm{coh}}\), an `.npz` file containing:

  - the ensemble of acceleration time series, and/or
  - the ensemble-averaged PSD used to compute \(A\) and \(\omega_c\).

The precise contents are documented in `TESTING.md`.

---

## Numerical checks

A separate `TESTING.md` file documents:

- Convergence checks in `n_steps` and `n_ensembles`.
- Sensitivity of \(\beta\) to the slip prefactor \(k\).
- Comparisons with known telegraph-noise scaling predictions (\(\beta \approx \alpha/2\) for \(q(W_{\mathrm{coh}}) \propto W_{\mathrm{coh}}^{-\alpha}\)).

If you modify the kernel or the YAML configuration, you can re-run the tests and add short notes to `TESTING.md` describing any changes.

---

## Relation to the BCQM IV_c paper

This code is intended as the **companion implementation** to the BCQM IV_c paper:

> _Boundary-Condition Quantum Mechanics IV_c: Diffusive inertia and the limits of binary hop kernels_,  
> Peter M. Ferguson, (Year, DOI to be added).

Every figure and numerical claim involving the **single-thread soft-rudder model** in IV_c should be reproducible by:

1. editing or copying the reference YAML configuration(s),
2. running the CLI as above, and
3. plotting the resulting CSV / `.npz` outputs.

---

## Citation

If you use this code in academic work, please cite the BCQM IV_c paper and, if applicable, the Zenodo record for this repository (once minted). A template BibTeX entry might look like:

```bibtex
@misc{Ferguson_BCQM_IVc_code,
  author       = {Peter M. Ferguson},
  title        = {{BCQM IV\_c soft-rudder single-thread inertial-noise code}},
  year         = {2025},
  howpublished = {\url{<Zenodo-URL-or-github-URL>}},
  note         = {Companion code to "Boundary-Condition Quantum Mechanics IV\_c: Diffusive inertia and the limits of binary hop kernels"}
}
```

Update the year, URL and (when available) DOI as appropriate.

---

## License

This code is released under the MIT License. See LICENSE for details.
